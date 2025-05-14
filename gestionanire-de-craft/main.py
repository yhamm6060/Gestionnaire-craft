import customtkinter as ctk
import sqlite3
from init_db import App as InitDBApp
from PIL import Image  # Assurez-vous que Pillow est installé : pip install pillow
#si la bdd ce met pas a jour et que la db est pas cree a dans le meme dossier du projet il faut changer le chemin dans la console vscode
# Initialiser l'application
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Système de Craft Dynamique")
        self.geometry("800x500")

        # Initialiser la base de données et charger les données
        self.init_db()
        self.table_data = {}
        self.craft_recipes = self.load_craft_recipes()

        # Création du cadre principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Navbar (barre de navigation)
        self.navbar = ctk.CTkFrame(self.main_frame, height=50)
        self.navbar.pack(side="top", fill="x", padx=10, pady=5)
        self.create_navbar_buttons()

        # Zone pour les écrans (soit accueil, soit gestion)
        self.content_frame = ctk.CTkFrame(self.main_frame)
        # Pour l'écran d'accueil, occupe toute la largeur.
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Afficher uniquement l'écran d'accueil au lancement
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
        home_button = ctk.CTkButton(
            self.navbar, 
            text="Home", 
            command=lambda: self.show_frame("home")
        )
        home_button.pack(side="left", padx=10, pady=10)

        # Remplacer le bouton avec image par un bouton texte simple
        craft_button = ctk.CTkButton(
            self.navbar,
            text="Gestionnaire de craft",
            command=lambda: self.show_frame("craft")
        )
        craft_button.pack(side="left", padx=10, pady=10)

        about_button = ctk.CTkButton(
            self.navbar, 
            text="About", 
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

        # Bouton pour accéder au gestionnaire de craft
        craft_manager_button = ctk.CTkButton(
            home_frame, 
            text="Accéder au gestionnaire de craft", 
            command=lambda: self.show_frame("craft")
        )
        craft_manager_button.pack(pady=10)


    def show_frame(self, frame_name):
        """Affiche l'écran correspondant (accueil ou gestionnaire de craft)."""
        # Vider le contenu de content_frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # Détruire la sidebar si elle existe déjà
        if hasattr(self, 'sidebar_frame'):
            self.sidebar_frame.destroy()

        if frame_name == "home":
            # Pour l'accueil, content_frame occupe toute la largeur.
            self.content_frame.pack_forget()
            self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
            self.create_home_frame()
        elif frame_name == "craft":
            # Créer la sidebar
            self.sidebar_frame = ctk.CTkFrame(self.main_frame, width=150)
            self.sidebar_frame.pack(side="left", fill="y", padx=10, pady=10)
            self.create_sidebar()
            # Repack content_frame à droite de la sidebar
            self.content_frame.pack_forget()
            self.content_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            # Création des tableaux
            self.create_first_table()
            self.separator = ctk.CTkLabel(self.content_frame, text="")
            self.separator.pack(pady=10)
            self.create_second_table()


    def about_button_pressed(self):
        print("Bouton About pressé")

    def create_first_table(self):
        table_frame = ctk.CTkScrollableFrame(self.content_frame)
        table_frame.pack(pady=10, fill="both", expand=True)

        title_label = ctk.CTkLabel(table_frame, text="Sélectionnez les objets à crafter", font=ctk.CTkFont(size=14, weight="bold"))
        title_label.pack(pady=5)

        # Trier les items par leur nom
        sorted_items = sorted(self.table_data.items(), key=lambda x: x[0].lower())  # Trie par nom (en minuscules pour ignorer la casse)

        self.row_frames = {}
        for item, data in sorted_items:
            row_frame = ctk.CTkFrame(table_frame)
            row_frame.pack(fill="x", padx=10, pady=2)
            self.row_frames[item] = row_frame

            label = ctk.CTkLabel(row_frame, text=item, width=200)
            label.pack(side="left", padx=5, pady=5, anchor="w")

            quantity_entry = ctk.CTkEntry(row_frame, width=50)
            quantity_entry.pack(side="left", padx=5, pady=5)

            quantity_entry.insert(0, "0")
            quantity_entry.bind("<KeyRelease>", lambda event, item=item, entry=quantity_entry: self.update_quantity(item, entry))

            favorite_checkbox = ctk.CTkCheckBox(row_frame, text="Favori", command=lambda item=item: self.toggle_favorite(item))
            favorite_checkbox.pack(side="right", padx=5, pady=5)

            if self.table_data[item]['favorite']:
                favorite_checkbox.select()
            else:
                favorite_checkbox.deselect()

    def toggle_favorite(self, item):
        """Modifié pour sauvegarder l'état dans la base de données"""
        self.table_data[item]['favorite'] = not self.table_data[item]['favorite']
        self.save_favorite(item, self.table_data[item]['favorite'])
        
        # Mettre à jour l'affichage après modification
        self.update_first_table()


    def update_first_table(self, event=None):
        search_term = self.search_var.get().lower()
        selected_category = self.category_var.get()
        show_favorites = self.favorite_filter.get()  # Vérifier si l'utilisateur veut filtrer par favoris

        for row_frame in self.row_frames.values():
            row_frame.pack_forget()  # Cacher toutes les lignes

        filtered_items = []
        for item, data in self.table_data.items():
            is_favorite = data.get('favorite', False)
            if (
                (search_term in item.lower() or search_term == "") and
                (selected_category == "Tous" or self.table_data[item]['category'] == selected_category) and
                (not show_favorites or is_favorite)  # Ne montrer que les favoris si le filtre est activé
            ):
                filtered_items.append(item)

        sorted_filtered_items = sorted(filtered_items, key=lambda x: x.lower())

        for item in sorted_filtered_items:
            row_frame = self.row_frames[item]
            row_frame.pack(fill="x", padx=10, pady=2)


    def create_second_table(self):
            """Crée le tableau affichant les ressources nécessaires en fonction des crafts sélectionnés."""
            self.second_table_frame = ctk.CTkFrame(self.content_frame)
            self.second_table_frame.pack(pady=10, fill="both", expand=True)

            title_label = ctk.CTkLabel(
                self.second_table_frame, 
                text="Résultats du Craft", 
                font=ctk.CTkFont(size=14, weight="bold")
            )
            title_label.pack(pady=5)

            self.second_table_data = self.calculate_resources_needed()
            for resource, quantity in self.second_table_data.items():
                resource_row = ctk.CTkFrame(self.second_table_frame)
                resource_row.pack(fill="x", padx=10, pady=2)

                resource_label = ctk.CTkLabel(resource_row, text=resource, width=200)
                resource_label.pack(side="left", padx=5, pady=5, anchor="w")

                quantity_label = ctk.CTkLabel(resource_row, text=str(quantity))
                quantity_label.pack(side="left", padx=5, pady=5)

    def calculate_resources_needed(self):
        """
        Calcule les ressources nécessaires en ne prenant en compte que les crafts dont la quantité est > 0.
        Chaque ressource est multipliée par la quantité sélectionnée pour le craft.
        """
        resources = {}
        for craft, ingredients in self.craft_recipes.items():
            # Récupérer la quantité saisie pour ce craft
            qty = self.table_data.get(craft, {}).get('quantity', 0)
            try:
                qty = int(qty)
            except ValueError:
                qty = 0
            if qty > 0:
                for ingredient, amount in ingredients.items():
                    resources[ingredient] = resources.get(ingredient, 0) + amount * qty


        return resources
    def update_quantity(self, item, entry):
        """Mise à jour de la quantité pour le craft et rafraîchissement du tableau des ressources."""
        try:
            new_qty = int(entry.get())
        except ValueError:
            new_qty = 0
        self.table_data[item]['quantity'] = new_qty
        self.refresh_second_table()

    def refresh_second_table(self):
        """Efface et recrée le tableau des résultats du craft."""
        if hasattr(self, 'second_table_frame') and self.second_table_frame is not None:
            self.second_table_frame.destroy()
        self.create_second_table()
# Lancer l'application
if __name__ == "__main__":
    app = App()
    app.mainloop()
