import customtkinter as ctk
import sqlite3
import tkinter.messagebox as tkmb
from init_db import App as InitDBApp
import json
import os
from datetime import datetime

# Initialiser l'application
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- Paramètres de pagination ---
CRAFTS_PER_PAGE = 20
CACHE_FILE = "craft_cache.json"

class CraftCache:
    """Gestionnaire de cache pour optimiser les performances"""
    
    def __init__(self, db_name="Crafts.db"):
        self.db_name = db_name
        self.cache_file = CACHE_FILE
        self.cache_data = None
        self.last_db_modified = None
        
    def get_db_modification_time(self):
        """Récupère la date de dernière modification de la base de données"""
        try:
            return os.path.getmtime(self.db_name)
        except OSError:
            return 0
    
    def is_cache_valid(self):
        """Vérifie si le cache est encore valide"""
        if not os.path.exists(self.cache_file):
            return False
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_info = json.load(f)
            
            cache_timestamp = cache_info.get('timestamp', 0)
            db_timestamp = self.get_db_modification_time()
            
            return cache_timestamp >= db_timestamp
        except (json.JSONDecodeError, KeyError):
            return False
    
    def load_from_cache(self):
        """Charge les données depuis le cache"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            return cache_data.get('recipes', {}), cache_data.get('table_data', {})
        except (json.JSONDecodeError, FileNotFoundError):
            return None, None
    
    def save_to_cache(self, recipes, table_data):
        """Sauvegarde les données dans le cache"""
        cache_data = {
            'timestamp': self.get_db_modification_time(),
            'recipes': recipes,
            'table_data': table_data,
            'created_at': datetime.now().isoformat()
        }
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du cache: {e}")
    
    def invalidate_cache(self):
        """Invalide le cache (le supprime)"""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
        except OSError as e:
            print(f"Erreur lors de la suppression du cache: {e}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Système de Craft Dynamique")
        self.geometry("800x500")

        self.init_db()
        self.cache_manager = CraftCache()
        self.table_data = {}
        self.craft_recipes = {}
        
        # Chargement optimisé des données
        self.load_data_optimized()

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Navbar (barre de navigation)
        self.navbar = ctk.CTkFrame(self.main_frame, height=50)
        self.create_navbar_buttons()

        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.create_home_frame()

    def init_db(self):
        """Initialise la base de données."""
        db_app = InitDBApp()
        db_app.fn_init_db()

    def load_data_optimized(self):
        """Charge les données de manière optimisée avec cache"""
        # Vérifier si le cache est valide
        if self.cache_manager.is_cache_valid():
            print("Chargement depuis le cache...")
            recipes, table_data = self.cache_manager.load_from_cache()
            if recipes is not None and table_data is not None:
                self.craft_recipes = recipes
                self.table_data = table_data
                return
        
        # Si pas de cache valide, charger depuis la DB et créer le cache
        print("Chargement depuis la base de données...")
        self.craft_recipes = self.load_craft_recipes_from_db()
        self.cache_manager.save_to_cache(self.craft_recipes, self.table_data)

    def load_craft_recipes_from_db(self):
        """Charge les recettes depuis la base de données (méthode originale)"""
        db_name = "Crafts.db"
        recipes = {}
        VALID_CATEGORIES = [
            "Général", "Survie", "Menuiserie", "Électrique", 
            "Agriculture", "Pêche", "Trappeur", "Cuisine", 
            "Premiers Secours", "Travail du Métal", "Artisanat"
        ]
        try:
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()
                # Récupérer toutes les données de crafts en une seule requête
                cursor.execute("SELECT id, name, category, favorite FROM Craft")
                crafts = cursor.fetchall()
                # Créer une correspondance entre craft_id et craft_name
                craft_map = {}
                for craft in crafts:
                    craft_id, craft_name, craft_category, is_favorite = craft
                    recipes[craft_name] = {}
                    self.table_data[craft_name] = {
                        'quantity': 0,
                        'favorite': bool(is_favorite),
                        'category': craft_category if craft_category and craft_category in VALID_CATEGORIES else "Général"
                    }
                    craft_map[craft_id] = craft_name

                if craft_map:
                    # Récupérer tous les ingrédients en une seule requête
                    placeholders = ','.join('?' for _ in craft_map)
                    query = f"""
                        SELECT CraftIngredient.craft_id, Ingredient.name 
                        FROM CraftIngredient
                        JOIN Ingredient ON Ingredient.id = CraftIngredient.ingredient_id
                        WHERE CraftIngredient.craft_id IN ({placeholders})
                    """
                    cursor.execute(query, list(craft_map.keys()))
                    for craft_id, ingredient_name in cursor.fetchall():
                        craft_name = craft_map[craft_id]
                        recipes[craft_name][ingredient_name] = 1
        except sqlite3.Error as e:
            print(f"Une erreur s'est produite : {e}")
            return {}
        
        return recipes

    def invalidate_cache_and_reload(self):
        """Invalide le cache et recharge les données"""
        self.cache_manager.invalidate_cache()
        self.load_data_optimized()

    def save_favorite(self, item, is_favorite):
        """Sauvegarde l'état du favori dans la base de données et invalide le cache"""
        try:
            with sqlite3.connect("Crafts.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Craft 
                    SET favorite = ? 
                    WHERE name = ?
                """, (int(is_favorite), item))
                conn.commit()
            # Invalider le cache après modification
            self.cache_manager.invalidate_cache()
        except sqlite3.Error as error:
            print(f"Erreur lors de la sauvegarde du favori: {error}")

    def create_navbar_buttons(self):
        # Bouton Gestionnaire de craft
        craft_button = ctk.CTkButton(
            self.navbar,
            text="Gestionnaire de craft",
            command=lambda: self.show_frame("craft")
        )
        craft_button.pack(side="left", padx=10, pady=10)

        # Boutons d'ajout, modification et suppression de craft
        add_button = ctk.CTkButton(
            self.navbar,
            text="Ajouter un craft",
            command=self.open_add_craft_window
        )
        add_button.pack(side="left", padx=5, pady=10)

        edit_button = ctk.CTkButton(
            self.navbar,
            text="Modifier un craft",
            command=self.open_edit_craft_window
        )
        edit_button.pack(side="left", padx=5, pady=10)

        delete_button = ctk.CTkButton(
            self.navbar,
            text="Supprimer un craft",
            command=self.open_delete_craft_window
        )
        delete_button.pack(side="left", padx=5, pady=10)

        # Bouton de rechargement du cache (pour debug/maintenance)
        refresh_button = ctk.CTkButton(
            self.navbar,
            text="🔄",
            width=30,
            command=self.force_reload
        )
        refresh_button.pack(side="left", padx=5, pady=10)

        # Bouton À propos
        about_button = ctk.CTkButton(
            self.navbar, 
            text="À propos", 
            command=self.about_button_pressed
        )
        about_button.pack(side="left", padx=10, pady=10)

    def force_reload(self):
        """Force le rechargement des données depuis la base"""
        self.invalidate_cache_and_reload()
        # Rafraîchir l'interface si on est sur la page craft
        if hasattr(self, 'table_frame'):
            self.create_first_table()
            self.create_second_table()
        tkmb.showinfo("Rechargement", "Données rechargées depuis la base de données")

    # ... [Le reste des méthodes restent identiques, mais on ajoute l'invalidation du cache] ...

    def open_add_craft_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Ajouter un craft")
        win.geometry("350x300")
        win.transient(self)
        win.grab_set()

        # Créer un frame scrollable
        scroll_frame = ctk.CTkScrollableFrame(win)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        name_var = ctk.StringVar()
        category_var = ctk.StringVar()
        ingredients_var = ctk.StringVar()

        categories = [
            "Artisanat", "Général", "Survie", "Menuiserie", 
            "Cuisine", "Électrique", "Premiers Secours", 
            "Travail du Métal", "Agriculture", "Pêche", "Trappeur"
        ]

        ctk.CTkLabel(scroll_frame, text="Nom du craft :").pack(pady=5)
        name_entry = ctk.CTkEntry(scroll_frame, textvariable=name_var)
        name_entry.pack(pady=5)

        category_var = ctk.StringVar(value=categories[0])
        ctk.CTkLabel(scroll_frame, text="Catégorie :").pack(pady=5)
        category_menu = ctk.CTkOptionMenu(scroll_frame, variable=category_var, values=categories)
        category_menu.pack(pady=5)

        ctk.CTkLabel(scroll_frame, text="Ingrédients (séparés par des virgules) :").pack(pady=5)
        ingredients_entry = ctk.CTkEntry(scroll_frame, textvariable=ingredients_var)
        ingredients_entry.pack(pady=5)

        def add_craft():
            name = name_var.get().strip()
            category = category_var.get().strip()
            ingredients = [i.strip() for i in ingredients_var.get().split(",") if i.strip()]
            if not name or not ingredients:
                return
            try:
                with sqlite3.connect("Crafts.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Craft (name, category, favorite) VALUES (?, ?, 0)", (name, category))
                    craft_id = cursor.lastrowid
                    for ing in ingredients:
                        cursor.execute("INSERT OR IGNORE INTO Ingredient (name) VALUES (?)", (ing,))
                        cursor.execute("SELECT id FROM Ingredient WHERE name = ?", (ing,))
                        ing_id = cursor.fetchone()[0]
                        cursor.execute("INSERT INTO CraftIngredient (craft_id, ingredient_id) VALUES (?, ?)", (craft_id, ing_id))
                    conn.commit()
                
                # Invalider le cache et recharger
                self.invalidate_cache_and_reload()
                self.create_first_table()
                self.create_second_table()
                tkmb.showinfo("Succès", "Le craft a bien été ajouté.")
                win.destroy()
            except Exception as e:
                print(e)

        ctk.CTkButton(scroll_frame, text="Ajouter", command=add_craft).pack(pady=10)

    def open_edit_craft_window(self):
        tkmb.showinfo("Info", "La modification de craft n'est pas encore implémentée.")

    def open_delete_craft_window(self):
        tkmb.showinfo("Info", "La suppression de craft n'est pas encore implémentée.")

    def create_sidebar(self):
        filter_label = ctk.CTkLabel(self.sidebar_frame, text="Filtres", font=ctk.CTkFont(size=16, weight="bold"))
        filter_label.pack(pady=10)

        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Recherche...", textvariable=self.search_var)
        search_entry.pack(pady=5, padx=10)
        search_entry.bind("<KeyRelease>", self.update_first_table)

        self.favorite_filter = ctk.CTkCheckBox(self.sidebar_frame, text="Favoris", command=self.update_first_table)
        self.favorite_filter.pack(pady=5)

        # Bouton Réinitialiser sous Favoris
        reset_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Réinitialiser",
            command=self.reset_all_crafts
        )
        reset_button.pack(pady=5, padx=10, fill="x")

        # Filtres par catégories
        category_label = ctk.CTkLabel(self.sidebar_frame, text="Catégories", font=ctk.CTkFont(size=14, weight="bold"))
        category_label.pack(pady=10)

        self.category_var = ctk.StringVar(value="Tous")

        categories = [
            "Tous",
            "Artisanat", "Général", "Survie", "Menuiserie", 
            "Cuisine", "Électrique", "Premiers Secours", 
            "Travail du Métal", "Agriculture", "Pêche", "Trappeur"
        ]

        for category in categories:
            radio_button = ctk.CTkRadioButton(
                self.sidebar_frame, 
                text=category, 
                variable=self.category_var, 
                value=category, 
                command=self.update_first_table
            )
            radio_button.pack(anchor="w", padx=10, pady=2)

    def create_home_frame(self):
        """Affiche un écran d'accueil avec un bouton pour accéder au gestionnaire de craft."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        home_frame = ctk.CTkFrame(self.content_frame)
        home_frame.pack(pady=10, padx=10, fill="both", expand=True)

        welcome_label = ctk.CTkLabel(
            home_frame, 
            text="Bienvenue dans le Système de Craft Dynamique", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        welcome_label.pack(pady=20)

        craft_manager_button = ctk.CTkButton(
            home_frame, 
            text="Accéder au gestionnaire de craft", 
            command=lambda: self.show_frame("craft")
        )
        craft_manager_button.pack(pady=10)

    def show_frame(self, frame_name):
        # Détruire la sidebar si elle existe déjà
        if hasattr(self, 'sidebar_frame') and self.sidebar_frame is not None:
            self.sidebar_frame.destroy()
            del self.sidebar_frame

        # Vider le contenu de content_frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if frame_name == "home":
            if self.navbar.winfo_ismapped():
                self.navbar.pack_forget()
            self.content_frame.pack_forget()
            self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
            self.create_home_frame()
        elif frame_name == "craft":
            if not self.navbar.winfo_ismapped():
                self.navbar.pack(side="top", fill="x", padx=10, pady=5)
            self.sidebar_frame = ctk.CTkFrame(self.main_frame, width=150)
            self.sidebar_frame.pack(side="left", fill="y", padx=10, pady=10)
            self.create_sidebar()
            self.content_frame.pack_forget()
            self.content_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            self.create_first_table()
            self.create_second_table()
        elif frame_name == "about":
            if not self.navbar.winfo_ismapped():
                self.navbar.pack(side="top", fill="x", padx=10, pady=5)
            self.content_frame.pack_forget()
            self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
            self.about_button_content()

    def about_button_pressed(self):
        self.show_frame("about")

    def about_button_content(self):
        """Affiche le contenu 'À propos' dans le content_frame principal."""
        about_frame = ctk.CTkFrame(self.content_frame)
        about_frame.pack(pady=10, padx=10, fill="both", expand=True)

        label = ctk.CTkLabel(
            about_frame,
            text=(
                "Gestionnaire de Craft Dynamique\n\n"
                "Cette application vous permet de :\n"
                "- Consulter et filtrer la liste des crafts disponibles\n"
                "- Marquer vos crafts favoris\n"
                "- Calculer automatiquement les ressources nécessaires selon les quantités\n"
                "- Réinitialiser rapidement toutes les quantités\n"
                "- Cache intelligent pour des performances optimisées\n\n"
                "Développé avec Python et CustomTkinter.\n"
                "Auteur : Hammouti Yassine \n"
                "Version : 1.1 (Optimisée)"
            ),
            justify="left",
            font=ctk.CTkFont(size=14)
        )
        label.pack(padx=20, pady=20, fill="both", expand=True)

    # [Le reste des méthodes comme create_first_table, update_first_table, etc. restent identiques]

    def create_first_table(self):
        """Crée les widgets une seule fois pour tous les crafts, sans pagination."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        if hasattr(self, 'table_frame') and self.table_frame is not None:
            self.table_frame.destroy()
            self.table_frame = None
        self.table_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.table_frame.pack(pady=10, fill="both", expand=True)

        title_label = ctk.CTkLabel(self.table_frame, text="Sélectionnez les objets à crafter", font=ctk.CTkFont(size=14, weight="bold"))
        title_label.pack(pady=5)

        self.row_frames = {}
        self.quantity_entries = {}
        self.favorite_checkboxes = {}
        self.craft_names_sorted = sorted(self.table_data.keys(), key=lambda x: x.lower())

        for item in self.craft_names_sorted:
            row_frame = self.create_craft_row(self.table_frame, item)
            row_frame.pack(fill="x", padx=10, pady=2)

        self.update_first_table()

    def update_first_table(self, event=None):
        """Affiche/masque les lignes selon les filtres, sans pagination."""
        search_term = self.search_var.get().lower()
        selected_category = self.category_var.get()
        show_favorites = self.favorite_filter.get()
        for item, row_frame in self.row_frames.items():
            visible = (
                (search_term in item.lower() or not search_term)
                and (selected_category == "Tous" or self.table_data[item]['category'] == selected_category)
                and (not show_favorites or self.table_data[item].get('favorite', False))
            )
            if visible:
                row_frame.pack(fill="x", padx=10, pady=2)
            else:
                row_frame.pack_forget()

    def update_quantity(self, item, entry):
        """Met à jour la quantité et seulement les labels concernés."""
        try:
            new_qty = int(entry.get())
        except ValueError:
            new_qty = 0
        self.table_data[item]['quantity'] = new_qty
        self.update_second_table_labels()

    def create_second_table(self):
        """Crée le tableau des résultats (labels uniquement, pas de destruction)."""
        if hasattr(self, 'second_table_frame') and self.second_table_frame is not None:
            self.second_table_frame.destroy()
            self.second_table_frame = None
        self.second_table_frame = ctk.CTkScrollableFrame(self.content_frame, height=200)
        self.second_table_frame.pack(pady=10, fill="both", expand=True)

        title_label = ctk.CTkLabel(
            self.second_table_frame, 
            text="Résultats du Craft", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=5)

        self.second_table_labels = {}
        self.update_second_table_labels(init=True)

    def update_second_table_labels(self, init=False):
        """Met à jour uniquement les labels des ressources nécessaires."""
        resources = self.calculate_resources_needed()
        if init:
            self.second_table_labels = {}
            for resource, quantity in resources.items():
                resource_row, quantity_label = self.create_resource_row(self.second_table_frame, resource, quantity)
                self.second_table_labels[resource] = quantity_label
        else:
            for resource, quantity in resources.items():
                if resource in self.second_table_labels:
                    self.second_table_labels[resource].configure(text=str(quantity))
                else:
                    resource_row, quantity_label = self.create_resource_row(self.second_table_frame, resource, quantity)
                    self.second_table_labels[resource] = quantity_label
            for resource in list(self.second_table_labels.keys()):
                if resource not in resources:
                    self.second_table_labels[resource].master.destroy()
                    del self.second_table_labels[resource]

    def reset_all_crafts(self):
        """Réinitialise toutes les quantités de crafts à zéro et rafraîchit les tableaux."""
        for item in self.table_data:
            self.table_data[item]['quantity'] = 0
        if hasattr(self, 'quantity_entries'):
            for entry in self.quantity_entries.values():
                entry.delete(0, "end")
                entry.insert(0, "0")
        self.update_second_table_labels()

    def calculate_resources_needed(self):
        """
        Calcule les ressources nécessaires en fonction des quantités de chaque craft.
        Retourne un dictionnaire {nom_ressource: quantité_totale}.
        """
        resources = {}
        for craft, data in self.table_data.items():
            qty = data.get('quantity', 0)
            if qty > 0 and craft in self.craft_recipes:
                for ingredient, ing_qty in self.craft_recipes[craft].items():
                    resources[ingredient] = resources.get(ingredient, 0) + ing_qty * qty
        return resources

    def create_resource_row(self, parent, resource, quantity):
        """Crée une ligne pour une ressource dans la seconde table."""
        resource_row = ctk.CTkFrame(parent)
        resource_row.pack(fill="x", padx=10, pady=2)
        resource_label = ctk.CTkLabel(resource_row, text=resource, width=200)
        resource_label.pack(side="left", padx=5, pady=5, anchor="w")
        quantity_label = ctk.CTkLabel(resource_row, text=str(quantity))
        quantity_label.pack(side="left", padx=5, pady=5)
        return resource_row, quantity_label

    def create_craft_row(self, parent, item):
        """Crée une ligne pour un craft dans la première table."""
        row_frame = ctk.CTkFrame(parent)
        label = ctk.CTkLabel(row_frame, text=item, width=200)
        label.pack(side="left", padx=5, pady=5, anchor="w")

        quantity_entry = ctk.CTkEntry(row_frame, width=50)
        quantity_entry.pack(side="left", padx=5, pady=5)
        quantity_entry.insert(0, str(self.table_data[item]['quantity']))
        quantity_entry.bind("<KeyRelease>", lambda event, item=item, entry=quantity_entry: self.update_quantity(item, entry))
        self.quantity_entries[item] = quantity_entry

        favorite_checkbox = ctk.CTkCheckBox(row_frame, text="Favori", command=lambda item=item: self.toggle_favorite(item))
        favorite_checkbox.pack(side="right", padx=5, pady=5)
        self.favorite_checkboxes[item] = favorite_checkbox
        if self.table_data[item]['favorite']:
            favorite_checkbox.select()
        else:
            favorite_checkbox.deselect()

        self.row_frames[item] = row_frame
        return row_frame

    def toggle_favorite(self, item):
        """Active/désactive le favori et sauvegarde en base."""
        current = self.table_data[item]['favorite']
        self.table_data[item]['favorite'] = not current
        self.save_favorite(item, not current)
        self.update_first_table()

# Lancer l'application
if __name__ == "__main__":
    app = App()
    app.mainloop()