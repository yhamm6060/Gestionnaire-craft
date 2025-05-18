import customtkinter as ctk
import sqlite3
import tkinter.messagebox as tkmb
from init_db import App as InitDBApp
#si la bdd ce met pas a jour et que la db est pas cree a dans le meme dossier du projet il faut changer le chemin dans la console vscode
# Initialiser l'application
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- Paramètres de pagination ---
CRAFTS_PER_PAGE = 20

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Système de Craft Dynamique")
        self.geometry("800x500")

        self.init_db()
        self.table_data = {}
        self.craft_recipes = self.load_craft_recipes()

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Navbar (barre de navigation)
        self.navbar = ctk.CTkFrame(self.main_frame, height=50)
        self.create_navbar_buttons()
        # NE PAS pack ici !

        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.create_home_frame()


    def init_db(self):
        """Initialise la base de données."""
        db_app = InitDBApp()
        db_app.fn_init_db()



    def load_craft_recipes(self):
        """Récupère les recettes et les favoris de la base de données de manière optimisée."""
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

    def save_favorite(self, item, is_favorite):
        """Sauvegarde l'état du favori dans la base de données"""
        try:
            with sqlite3.connect("Crafts.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Craft 
                    SET favorite = ? 
                    WHERE name = ?
                """, (int(is_favorite), item))
                conn.commit()
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

        # Bouton À propos
        about_button = ctk.CTkButton(
            self.navbar, 
            text="À propos", 
            command=self.about_button_pressed
        )
        about_button.pack(side="left", padx=10, pady=10)

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

        self.category_var = ctk.StringVar(value="Tous")  # Valeur par défaut

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
        # Vider le contenu existant
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
                "- Réinitialiser rapidement toutes les quantités\n\n"
                "Développé avec Python et CustomTkinter.\n"
                "Auteur : Hammouti Yassine \n"
                "Version : 1.0"
            ),
            justify="left",
            font=ctk.CTkFont(size=14)
        )
        label.pack(padx=20, pady=20, fill="both", expand=True)

    def create_first_table(self):
        """Crée les widgets une seule fois pour tous les crafts, sans pagination."""
        # Vider tout le contenu du content_frame pour éviter la multiplication des tableaux
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # Détruire l'ancien tableau s'il existe
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

    def next_page(self):
        self.show_page(self.current_page + 1)

    def prev_page(self):
        self.show_page(self.current_page - 1)

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
        # Détruire l'ancien tableau s'il existe
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
            # Met à jour ou crée les labels si besoin
            for resource, quantity in resources.items():
                if resource in self.second_table_labels:
                    self.second_table_labels[resource].configure(text=str(quantity))
                else:
                    resource_row, quantity_label = self.create_resource_row(self.second_table_frame, resource, quantity)
                    self.second_table_labels[resource] = quantity_label
            # Supprime les ressources qui ne sont plus nécessaires
            for resource in list(self.second_table_labels.keys()):
                if resource not in resources:
                    self.second_table_labels[resource].master.destroy()
                    del self.second_table_labels[resource]

    def reset_all_crafts(self):
        """Réinitialise toutes les quantités de crafts à zéro et rafraîchit les tableaux."""
        for item in self.table_data:
            self.table_data[item]['quantity'] = 0
        # Remettre à zéro les champs d'entrée visuellement
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

    def open_add_craft_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Ajouter un craft")
        win.geometry("350x300")

        name_var = ctk.StringVar()
        category_var = ctk.StringVar()
        ingredients_var = ctk.StringVar()

        categories = [
            "Artisanat", "Général", "Survie", "Menuiserie", 
            "Cuisine", "Électrique", "Premiers Secours", 
            "Travail du Métal", "Agriculture", "Pêche", "Trappeur"
        ]

        ctk.CTkLabel(win, text="Nom du craft :").pack(pady=5)
        name_entry = ctk.CTkEntry(win, textvariable=name_var)
        name_entry.pack(pady=5)

        categories = [
            "Artisanat", "Général", "Survie", "Menuiserie", 
            "Cuisine", "Électrique", "Premiers Secours", 
            "Travail du Métal", "Agriculture", "Pêche", "Trappeur"
        ]
        category_var = ctk.StringVar(value=categories[0])
        ctk.CTkLabel(win, text="Catégorie :").pack(pady=5)
        category_menu = ctk.CTkOptionMenu(win, variable=category_var, values=categories)
        category_menu.pack(pady=5)

        ctk.CTkLabel(win, text="Ingrédients (séparés par des virgules) :").pack(pady=5)
        ingredients_entry = ctk.CTkEntry(win, textvariable=ingredients_var)
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
                self.craft_recipes = self.load_craft_recipes()
                self.create_first_table()
                self.create_second_table()
                tkmb.showinfo("Succès", "Le craft a bien été ajouté.")
                win.destroy()
            except Exception as e:
                print(e)

        ctk.CTkButton(win, text="Ajouter", command=add_craft).pack(pady=10)

    def open_edit_craft_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Modifier un craft")
        win.geometry("350x400")

        craft_names = list(self.table_data.keys())
        filtered_crafts = craft_names.copy()
        selected_craft = ctk.StringVar(value=craft_names[0] if craft_names else "")

        # Barre de recherche
        search_var = ctk.StringVar()
        def update_craft_menu(*_):
            search = search_var.get().lower()
            filtered = [name for name in craft_names if search in name.lower()]
            craft_menu.configure(values=filtered)
            if filtered:
                selected_craft.set(filtered[0])
            else:
                selected_craft.set("")
        ctk.CTkLabel(win, text="Rechercher un craft :").pack(pady=5)
        search_entry = ctk.CTkEntry(win, textvariable=search_var)
        search_entry.pack(pady=5)
        search_var.trace_add("write", update_craft_menu)

        ctk.CTkLabel(win, text="Sélectionnez un craft :").pack(pady=5)
        craft_menu = ctk.CTkOptionMenu(win, variable=selected_craft, values=filtered_crafts)
        craft_menu.pack(pady=5)

        name_var = ctk.StringVar()
        category_var = ctk.StringVar()
        ingredients_var = ctk.StringVar()

        categories = [
            "Artisanat", "Général", "Survie", "Menuiserie", 
            "Cuisine", "Électrique", "Premiers Secours", 
            "Travail du Métal", "Agriculture", "Pêche", "Trappeur"
        ]

        def fill_fields(*_):
            name = selected_craft.get()
            name_var.set(name)
            category_var.set(self.table_data[name]['category'])
            ingredients = list(self.craft_recipes.get(name, {}).keys())
            ingredients_var.set(", ".join(ingredients))

        fill_fields()
        craft_menu.configure(command=lambda _: fill_fields())

        ctk.CTkLabel(win, text="Nouveau nom :").pack(pady=5)
        name_entry = ctk.CTkEntry(win, textvariable=name_var)
        name_entry.pack(pady=5)

        ctk.CTkLabel(win, text="Nouvelle catégorie :").pack(pady=5)
        category_menu = ctk.CTkOptionMenu(win, variable=category_var, values=categories)
        category_menu.pack(pady=5)

        ctk.CTkLabel(win, text="Nouveaux ingrédients (séparés par des virgules) :").pack(pady=5)
        ingredients_entry = ctk.CTkEntry(win, textvariable=ingredients_var)
        ingredients_entry.pack(pady=5)

        def edit_craft():
            old_name = selected_craft.get()
            new_name = name_var.get().strip()
            new_category = category_var.get().strip()
            new_ingredients = [i.strip() for i in ingredients_var.get().split(",") if i.strip()]
            if not new_name or not new_ingredients:
                return
            try:
                with sqlite3.connect("Crafts.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM Craft WHERE name = ?", (old_name,))
                    craft_id = cursor.fetchone()[0]
                    cursor.execute("UPDATE Craft SET name = ?, category = ? WHERE id = ?", (new_name, new_category, craft_id))
                    cursor.execute("DELETE FROM CraftIngredient WHERE craft_id = ?", (craft_id,))
                    for ing in new_ingredients:
                        cursor.execute("INSERT OR IGNORE INTO Ingredient (name) VALUES (?)", (ing,))
                        cursor.execute("SELECT id FROM Ingredient WHERE name = ?", (ing,))
                        ing_id = cursor.fetchone()[0]
                        cursor.execute("INSERT INTO CraftIngredient (craft_id, ingredient_id) VALUES (?, ?)", (craft_id, ing_id))
                    conn.commit()
                self.craft_recipes = self.load_craft_recipes()
                self.create_first_table()
                self.create_second_table()
                tkmb.showinfo("Succès", "Le craft a bien été modifié.")
                win.destroy()
            except Exception as e:
                print(e)

        ctk.CTkButton(win, text="Modifier", command=edit_craft).pack(pady=10)

    def open_delete_craft_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Supprimer un craft")
        win.geometry("300x250")

        craft_names = list(self.table_data.keys())
        filtered_crafts = craft_names.copy()
        selected_craft = ctk.StringVar(value=craft_names[0] if craft_names else "")

        # Barre de recherche
        search_var = ctk.StringVar()
        def update_craft_menu(*_):
            search = search_var.get().lower()
            filtered = [name for name in craft_names if search in name.lower()]
            craft_menu.configure(values=filtered)
            if filtered:
                selected_craft.set(filtered[0])
            else:
                selected_craft.set("")
        ctk.CTkLabel(win, text="Rechercher un craft :").pack(pady=5)
        search_entry = ctk.CTkEntry(win, textvariable=search_var)
        search_entry.pack(pady=5)
        search_var.trace_add("write", update_craft_menu)

        ctk.CTkLabel(win, text="Sélectionnez un craft à supprimer :").pack(pady=10)
        craft_menu = ctk.CTkOptionMenu(win, variable=selected_craft, values=filtered_crafts)
        craft_menu.pack(pady=10)

        def delete_craft():
            name = selected_craft.get()
            if not name:
                ctk.CTkMessagebox.show_error("Erreur", "Aucun craft sélectionné.")
                return
            try:
                with sqlite3.connect("Crafts.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM Craft WHERE name = ?", (name,))
                    result = cursor.fetchone()
                    if not result:
                        ctk.CTkMessagebox.show_error("Erreur", "Craft introuvable.")
                        return
                    craft_id = result[0]
                    cursor.execute("DELETE FROM CraftIngredient WHERE craft_id = ?", (craft_id,))
                    cursor.execute("DELETE FROM Craft WHERE id = ?", (craft_id,))
                    conn.commit()
                self.craft_recipes = self.load_craft_recipes()
                self.create_first_table()
                self.create_second_table()
                win.destroy()
            except Exception as e:
                print(e)

        ctk.CTkButton(win, text="Supprimer", command=delete_craft).pack(pady=10)

    def create_resource_row(self, parent, resource, quantity):
        """Crée une ligne pour une ressource dans la seconde table."""
        resource_row = ctk.CTkFrame(parent)
        resource_row.pack(fill="x", padx=10, pady=2)
        resource_label = ctk.CTkLabel(resource_row, text=resource, width=200)
        resource_label.pack(side="left", padx=5, pady=5, anchor="w")
        quantity_label = ctk.CTkLabel(resource_row, text=str(quantity))
        quantity_label.pack(side="left", padx=5, pady=5)
        return resource_row, quantity_label

    def refresh_tables(self):
        self.create_first_table()
        self.create_second_table()

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
