import sqlite3
from sqlite3 import Error


class App:
    def fn_init_db(self):
        """Initialise la base de données et crée les tables si elles n'existent pas."""
        try:
            sqliteConnection = sqlite3.connect('Crafts.db')
            cursor = sqliteConnection.cursor()

            # Création de la table Craft avec la colonne category
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Craft (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'Général',
                    favorite INTEGER DEFAULT 0
                )
            """)

            # Vérification pour ajouter la colonne `category` si elle manque
            cursor.execute("PRAGMA table_info(Craft)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'category' not in columns:
                cursor.execute("ALTER TABLE Craft ADD COLUMN category TEXT DEFAULT 'Général'")

            # Création de la table Ingredient
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Ingredient (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)

            # Création de la table CraftIngredient avec la colonne quantité
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS CraftIngredient (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    craft_id INTEGER NOT NULL,
                    ingredient_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (craft_id) REFERENCES Craft(id),
                    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(id)
                )
            """)

            sqliteConnection.commit()
            print("Base de données initialisée avec succès")

        except Error as e:
            print(f"Erreur lors de l'initialisation de la base de données: {e}")

        finally:
            if sqliteConnection:
                sqliteConnection.close()

    def add_craft(self, craft_name, ingredients, category="Général"):
        """
        Ajoute un craft avec ses ingrédients, quantités et sa catégorie.
        
        Paramètres :
            - craft_name (str) : Nom du craft.
            - ingredients (list[tuple]) : Liste de tuples (nom_ingredient, quantité).
            - category (str) : Catégorie du craft.
        """
        try:
            sqliteConnection = sqlite3.connect('Crafts.db')
            cursor = sqliteConnection.cursor()

            # Vérification pour éviter les doublons de crafts
            cursor.execute("SELECT id FROM Craft WHERE name = ?", (craft_name,))
            craft = cursor.fetchone()
            if craft:
                print(f"Le craft '{craft_name}' existe déjà.")
                return

            # Insertion du craft avec la catégorie
            cursor.execute("INSERT INTO Craft (name, category) VALUES (?, ?)", (craft_name, category))
            craft_id = cursor.lastrowid

            # Traitement des ingrédients
            for ingredient_name, quantity in ingredients:
                if ingredient_name:
                    # Vérification pour éviter les doublons d'ingrédients
                    cursor.execute("SELECT id FROM Ingredient WHERE name = ?", (ingredient_name,))
                    ingredient = cursor.fetchone()
                    if ingredient:
                        ingredient_id = ingredient[0]
                    else:
                        cursor.execute("INSERT INTO Ingredient (name) VALUES (?)", (ingredient_name,))
                        ingredient_id = cursor.lastrowid

                    # Insertion dans CraftIngredient avec la quantité
                    cursor.execute("""
                        INSERT INTO CraftIngredient (craft_id, ingredient_id, quantity)
                        VALUES (?, ?, ?)
                    """, (craft_id, ingredient_id, quantity))

            sqliteConnection.commit()
            print(f"Craft '{craft_name}' ajouté avec succès avec ses ingrédients et quantités.")

        except Error as e:
            print(f"Erreur lors de l'ajout du craft: {e}")

        finally:
            if sqliteConnection:
                sqliteConnection.close()

    def load_craft_recipes(self):
        """
        Charge les recettes de craft depuis la base de données.
        
        Retourne :
            dict: Dictionnaire des recettes classées par catégorie.
        """
        db_name = "Crafts.db"
        recipes = {}
        try:
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT Craft.name, Craft.category, Ingredient.name, CraftIngredient.quantity
                    FROM Craft
                    JOIN CraftIngredient ON Craft.id = CraftIngredient.craft_id
                    JOIN Ingredient ON Ingredient.id = CraftIngredient.ingredient_id
                """)
                crafts = cursor.fetchall()

                for craft_name, category, ingredient_name, quantity in crafts:
                    if category not in recipes:
                        recipes[category] = {}
                    if craft_name not in recipes[category]:
                        recipes[category][craft_name] = {}
                    recipes[category][craft_name][ingredient_name] = quantity

        except sqlite3.Error as error:
            print(f"Erreur lors du chargement des recettes: {error}")

        return recipes


# Initialisation de l'application et de la base de données
app = App()
app.fn_init_db()

# Ajout de crafts et de leurs ingrédients

app.add_craft("Bandage",
              [("Tissu déchiré", 1), ("Eau", 1)],
              category="Premiers Secours")

app.add_craft("Tissu déchiré",
              [("Chiffon sale", 1), ("Eau", 1)],
              category="Premiers Secours")

app.add_craft("Lanières de cuir",
              [("Lanières de cuir sales", 1), ("Eau", 1)],
              category="Premiers Secours")

app.add_craft("Lanières de jean",
              [("Lanières de jean sales", 1), ("Eau", 1)],
              category="Premiers Secours")

app.add_craft("Bandage stérilisé",
              [("Bouteille de désinfectant", 3), ("Casserole d'eau", 1), ("Bandage", 1)],
              category="Premiers Secours")

app.add_craft("Chiffon stérilisé",
              [("Bouteille de désinfectant", 3), ("Casserole d'eau", 1), ("Tissu déchiré", 1)],
              category="Premiers Secours")

app.add_craft("Attelle",
              [("Planche", 1), ("Tissu déchiré", 1)],
              category="Premiers Secours")

app.add_craft("Attelle",
              [("Branche d'arbre", 1), ("Tissu déchiré", 1)],
              category="Premiers Secours")

app.add_craft("Attelle",
              [("Bâton robuste", 1), ("Tissu déchiré", 1)],
              category="Premiers Secours")

app.add_craft("Cotons imbibés d'alcool",
              [("Bouteille de désinfectant", 1), ("Cotons", 1)],
              category="Premiers Secours")


# Catégorie Travail du Métal
app.add_craft("Tuyau en métal",
              [("Chalumeau", 2)],
              category="Travail du Métal")


#categorie agriculture 

app.add_craft("Paquet de graines de brocoli",
              [("Graines de brocoli", 50)],
              category="Agriculture")

app.add_craft("Graines de brocoli",
              [("Paquet de graines de brocoli", 1)],
              category="Agriculture")

app.add_craft("Paquet de graines de chou",
              [("Graines de chou", 50)],
              category="Agriculture")

app.add_craft("Graines de chou",
              [("Paquet de graines de chou", 1)],
              category="Agriculture")

app.add_craft("Paquet de graines de carotte",
              [("Graines de carotte", 50)],
              category="Agriculture")

app.add_craft("Graines de carotte",
              [("Paquet de graines de carotte", 1)],
              category="Agriculture")

app.add_craft("Paquet de graines de pomme de terre",
              [("Graines de pomme de terre", 50)],
              category="Agriculture")

app.add_craft("Graines de pomme de terre",
              [("Paquet de graines de pomme de terre", 1)],
              category="Agriculture")

app.add_craft("Paquet de graines de radis",
              [("Graines de radis", 50)],
              category="Agriculture")

app.add_craft("Graines de radis",
              [("Paquet de graines de radis", 1)],
              category="Agriculture")

app.add_craft("Paquet de graines de fraise",
              [("Graines de fraise", 50)],
              category="Agriculture")

app.add_craft("Graines de fraise",
              [("Paquet de graines de fraise", 1)],
              category="Agriculture")

app.add_craft("Paquet de graines de tomate",
              [("Graines de tomate", 50)],
              category="Agriculture")

app.add_craft("Graines de tomate",
              [("Paquet de graines de tomate", 1)],
              category="Agriculture")
# Catégorie Trappeur
app.add_craft("Piège-cage",
              [("Fil de fer", 5)],
              category="Trappeur")

app.add_craft("Piège à lacet",
              [("Planche", 1), ("Corde", 2)],
              category="Trappeur")

app.add_craft("Piège à bâtons",
              [("Bâton robuste", 4), ("Corde", 2)],
              category="Trappeur")

app.add_craft("Piège boîte",
              [("Planche", 4), ("Clous", 7)],
              category="Trappeur")

app.add_craft("Piège caisse",
              [("Planche", 3), ("Clous", 5)],
              category="Trappeur")


# Catégorie peche
app.add_craft("Canne à pêche",
              [("Bâton robuste", 1)],
              category="Pêche")

app.add_craft("Canne à pêche",
              [("Bâton robuste", 1), ("Fil de pêche", 1), ("Clou", 1)],
              category="Pêche")

app.add_craft("Filet de pêche",
              [("Ficelle", 10), ("Fil de fer", 5)],
              category="Pêche")

app.add_craft("Fil de fer",
              [("Filet de pêche cassé", 1)],
              category="Pêche")


# Catégorie artisanat


app.add_craft(".223 Cartouche",
              [("Boîte de cartouches .223", 1)],
              category="Artisanat")

app.add_craft(".38 Cartouche Special",
              [("Boîte de cartouches .38 Special", 1)],
              category="Artisanat")

app.add_craft(".44 Cartouche Magnum",
              [("Boîte de cartouches .44 Magnum", 1)],
              category="Artisanat")

app.add_craft(".45 Cartouche Auto",
              [("Boîte de cartouches .45 Auto", 1)],
              category="Artisanat")

app.add_craft("5.56mm Cartouche",
              [("Boîte de cartouches 5.56mm", 1)],
              category="Artisanat")

# Outil requis : Scie ou Scie à métaux
app.add_craft("Bâton robuste",
              [("Planche", 1)],
              category="Artisanat")

app.add_craft("Boîte de cartouches .223",
              [(".223 Cartouche", 40)],
              category="Artisanat")

app.add_craft("Boîte de cartouches .38 Special",
              [(".38 Cartouche Special", 30)],
              category="Artisanat")

app.add_craft("Boîte de cartouches .44 Magnum",
              [(".44 Cartouche Magnum", 12)],
              category="Artisanat")

app.add_craft("Boîte de cartouches .45 Auto",
              [(".45 Cartouche Auto", 30)],
              category="Artisanat")

app.add_craft("Boîte de cartouches 5.56mm",
              [("5.56mm Cartouche", 60)],
              category="Artisanat")

app.add_craft("Boîte de cartouches 9 mm",
              [("Munitions de 9 mm", 30)],
              category="Artisanat")

app.add_craft("Boîte de bocaux",
              [("Pot vide", 6)],
              category="Artisanat")

app.add_craft("Boîte de clous",
              [("Clous", 100)],
              category="Artisanat")

app.add_craft("Boîte de trombones",
              [("Trombone", 40)],
              category="Artisanat")

app.add_craft("Boîte de vis",
              [("Vis", 100)],
              category="Artisanat")

app.add_craft("Boîte de cartouches de fusil",
              [("Cartouches calibre 12", 24)],
              category="Artisanat")

# Deux recettes possibles
app.add_craft("Bougie",
              [("Briquet", 1), ("Bougie", 1)],
              category="Artisanat")

app.add_craft("Bougie",
              [("Allumettes", 1), ("Bougie", 1)],
              category="Artisanat")

app.add_craft("Cartouches calibre 12",
              [("Boîte de cartouches de fusil", 1)],
              category="Artisanat")

app.add_craft("Vêtements propres",
              [("Vêtements", 1), ("Eau", 3), ("Savon", 1)],
              category="Artisanat")

app.add_craft("Vêtements propres",
              [("Vêtements", 1), ("Eau", 3), ("Liquide nettoyant", 1)],
              category="Artisanat")

# Cocktail Molotov - option 1
app.add_craft("Cocktail Molotov",
              [("Tissu déchiré", 1), ("Bouteille de Bourbon", 1)],
              category="Artisanat")

app.add_craft("Cocktail Molotov",
              [("Chiffon sale", 1), ("Bouteille de Bourbon", 1)],
              category="Artisanat")

# Cocktail Molotov - option 2
app.add_craft("Cocktail Molotov",
              [("Bouteille vide", 3), ("Tissu déchiré", 1), ("Bidon d’essence", 1)],
              category="Artisanat")

app.add_craft("Cocktail Molotov",
              [("Bouteille vide", 3), ("Chiffon sale", 1), ("Bidon d’essence", 1)],
              category="Artisanat")

# Ingrédient alternatif Drap ou Vêtement (coton)
app.add_craft("Corde de draps",
              [("Drap", 1)],
              category="Artisanat")

app.add_craft("Corde de draps",
              [("Vêtement (coton)", 1)],
              category="Artisanat")

# Outil requis : Ciseaux
app.add_craft("Bande de jean",
              [("Vêtement (denim)", 1)],
              category="Artisanat")

app.add_craft("Pot vide",
              [("Boîte de bocaux", 1)],
              category="Artisanat")

# Outil requis : Scie ou Scie à métaux
app.add_craft("Fusil à canon scié (JS-2000)",
              [("Fusil à pompe", 1)],
              category="Artisanat")

# Multi-ingrédients alternatifs
app.add_craft("Poudre à canon",
              [(".38 Cartouche Special", 1)],
              category="Artisanat")
app.add_craft("Poudre à canon",
              [(".44 Cartouche Magnum", 1)],
              category="Artisanat")
app.add_craft("Poudre à canon",
              [(".45 Cartouche Auto", 1)],
              category="Artisanat")
app.add_craft("Poudre à canon",
              [("Munitions de 9 mm", 1)],
              category="Artisanat")
app.add_craft("Poudre à canon",
              [("5.56mm Cartouche", 1)],
              category="Artisanat")
app.add_craft("Poudre à canon",
              [(".308 Cartouche", 1)],
              category="Artisanat")
app.add_craft("Poudre à canon",
              [(".223 Cartouche", 1)],
              category="Artisanat")
app.add_craft("Poudre à canon",
              [("Cartouches calibre 12", 1)],
              category="Artisanat")

app.add_craft("Lampe torche manuelle",
              [("Lampe torche", 1), ("Pile", 1)],
              category="Artisanat")

app.add_craft("Lampe de poche",
              [("Lampe de poche", 1), ("Pile", 1)],
              category="Artisanat")

# Outil requis : Ciseaux
app.add_craft("Bande de cuir",
              [("Vêtement (cuir)", 1)],
              category="Artisanat")

app.add_craft("Munitions de 9 mm",
              [("Boîte de cartouches 9 mm", 1)],
              category="Artisanat")

app.add_craft("Chapeau en journal",
              [("Journal", 1)],
              category="Artisanat")

# Outil requis : Tournevis ou Couteau
app.add_craft("Planche rainurée",
              [("Planche", 1)],
              category="Artisanat")

app.add_craft("Planche rainurée",
              [("Bûche", 1)],
              category="Artisanat")

# Multi-ingrédients
app.add_craft("Pile",
              [("Lampe de poche", 1)],
              category="Artisanat")
app.add_craft("Pile",
              [("Lampe torche", 1)],
              category="Artisanat")
app.add_craft("Pile",
              [("Canard en plastique", 1)],
              category="Artisanat")

app.add_craft("Canard en plastique",
              [("Canard en plastique", 1), ("Pile", 1)],
              category="Artisanat")

# Outil requis : Scie ou Scie à métaux
app.add_craft("Fusil à double canon scié",
              [("Fusil à double canon", 1)],
              category="Artisanat")

app.add_craft("Vis",
              [("Boîte de vis", 1)],
              category="Artisanat")

app.add_craft("Bouteille brisée",
              [("Bouteille vide", 4)],
              category="Artisanat")

app.add_craft("Chapeau en aluminium",
              [("Papier aluminium", 1)],
              category="Artisanat")

# XP : 0.25 en Couture
app.add_craft("Tissu déchiré",
              [("Drap", 1)],
              category="Artisanat")

app.add_craft("Tissu déchiré",
              [("Vêtement (coton)", 1)],
              category="Artisanat")

app.add_craft("Parapluie",
              [("Parapluie fermé", 1)],
              category="Artisanat")

app.add_craft("Parapluie fermé",
              [("Parapluie", 1)],
              category="Artisanat")

# Catégorie Cuisine

app.add_craft("Bouteille vide (Bourbon)",
              [("Bouteille de Bourbon", 1)],
              category="Cuisine")

app.add_craft("Poêle à frire",
              [("Sauté", 1)],
              category="Cuisine")

app.add_craft("Gril",
              [("Sauté", 1)],
              category="Cuisine")

app.add_craft("Plat à rôtir",
              [("Légumes rôtis", 1)],
              category="Cuisine")

app.add_craft("Sucette",
              [("Paquet de bonbons", 1)],
              category="Cuisine")

app.add_craft("Œuf",
              [("Carton d'œufs", 1)],
              category="Cuisine")

app.add_craft("Carton d'œufs",
              [("Œuf", 12)],
              category="Cuisine")







# Catégorie Général
app.add_craft("Poudre à canon",
              [("Boîte de munitions 40 cal", 1), ("Munitions Rifle .308 loose", 1), ("Cartouches de fusil", 1)],
              category="Général")
app.add_craft("Lampe de poche", [("Lampe de poche", 1), ("Pile", 1)], category="Général")
app.add_craft("Pile", [("Lampe de poche", 1), ("Torche à main", 1), ("Canard en caoutchouc", 1)], category="Général")
app.add_craft("Bougie", [("Briquet", 1), ("Allumettes", 1), ("Bougie", 1)], category="Général")
app.add_craft("Tissu déchiré", [("Vêtements (coton)", 1), ("Drap", 1)], category="Général")
app.add_craft("Corde de draps", [("Drap", 1), ("Vêtements (coton)", 1)], category="Général")
app.add_craft("Cocktail Molotov", [("Tissu déchiré", 1), ("Tissu sale", 1), ("Bouteille de Bourbon", 1)],
              category="Général")
app.add_craft("Cocktail Molotov", [("Bouteille vide de whisky", 1), ("Bouteille vide de vin", 1),
                                    ("Bouteille vide de vin 2", 1), ("Tissu déchiré", 1), ("Pétrole", 1)],
              category="Général")
app.add_craft("Munitions de fusil", [("Boîte de cartouches de fusil", 1)], category="Général")
app.add_craft("Clous", [("Boîte de clous", 1)], category="Général")
app.add_craft("Vis", [("Boîte de vis", 1)], category="Général")
app.add_craft("Trombones", [("Boîte de trombones", 1)], category="Général")
app.add_craft("Bocal", [("Boîte de bocaux", 1)], category="Général")
app.add_craft("Vêtements propres",
              [("Savon", 1), ("Liquide de nettoyage", 1), ("Gouttes d'eau", 3)],
              category="Général")
app.add_craft("Parapluie", [("Parapluie fermé", 1)], category="Général")
app.add_craft("Planches de bois", [("Planche", 1), ("Bûche", 1)], category="Général")
app.add_craft("Canard en caoutchouc", [("Canard en caoutchouc", 1), ("Pile", 1)], category="Général")
app.add_craft("Torche à main", [("Torche à main", 1), ("Pile", 1)], category="Général")
app.add_craft("Chapeau de journal", [("Journal", 1)], category="Général")
app.add_craft("Chapeau en aluminium", [("Aluminium", 1)], category="Général")
app.add_craft("Bâton robuste", [("Planche", 1)], category="Général")
app.add_craft("Fusil", [("Fusil à pompe", 1), ("Scie de jardin", 1)], category="Général")
app.add_craft("Fusil à canon scié", [("Fusil à canon scié", 1), ("Scie de jardin", 1)], category="Général")
app.add_craft("Bouteille brisée", [("Bouteille vide de vin", 1), ("Bouteille vide de whisky", 1),
                                   ("Bouteille de bière", 1)], category="Général")

# Catégorie Survie
app.add_craft("Feu de camp",
              [("Brindilles", 1), ("Drap", 1), ("Tissu déchiré", 1), ("Tissu sale", 1),
               ("Livre", 1), ("Magazine", 1), ("Journal", 1), ("Bûche", 2)],
              category="Survie")
app.add_craft("Feu de camp",
              [("Brindilles", 1), ("Drap", 1), ("Tissu déchiré", 1), ("Tissu sale", 1),
               ("Livre", 1), ("Magazine", 1), ("Journal", 1), ("Planche", 3)],
              category="Survie")
app.add_craft("Kit de tente",
              [("Toile", 1), ("Piquet de tente", 4), ("Bâton robuste", 2)],
              category="Survie")
app.add_craft("Kit de tente",
              [("Toile", 1), ("Piquet", 4), ("Bâton robuste", 2)],
              category="Survie")
app.add_craft("Piquet",
              [("Couteau en pierre", 1), ("Couteau de chasse", 1), ("Couteau de cuisine", 1),
               ("Couteau à viande", 1), ("Machette", 1), ("Branche", 1)],
              category="Survie")
app.add_craft("Couteau en pierre",
              [("Tissu déchiré", 1), ("Tissu sale", 1), ("Fil", 1), ("Branche", 1), ("Pierre aiguisée", 1)],
              category="Survie")
app.add_craft("Hache en pierre",
              [("Tissu déchiré", 1), ("Tissu sale", 1), ("Fil", 1), ("Branche", 1), ("Pierre aiguisée", 1)],
              category="Survie")
app.add_craft("Marteau en pierre",
              [("Tissu déchiré", 1), ("Tissu sale", 1), ("Fil", 1), ("Branche", 1), ("Pierre", 1)],
              category="Survie")
app.add_craft("Lance",
              [("Branche", 1), ("Planche", 1), ("Couteau de cuisine", 1),
               ("Machette", 1), ("Couteau à viande", 1), ("Couteau en pierre", 1)],
              category="Survie")
app.add_craft("Lance avec couteau à pain",
              [("Lance", 1), ("Couteau à pain", 1), ("Ruban adhésif", 2)],
              category="Survie")
app.add_craft("Lance avec couteau à beurre",
              [("Lance", 1), ("Couteau à beurre", 1), ("Ruban adhésif", 1)],
              category="Survie")
app.add_craft("Lance avec fourchette",
              [("Lance", 1), ("Fourchette", 1), ("Ruban adhésif", 2)],
              category="Survie")
app.add_craft("Lance avec ouvre-lettres",
              [("Lance", 1), ("Ouvre-lettres", 1), ("Ruban adhésif", 2)],
              category="Survie")
app.add_craft("Lance avec scalpel",
              [("Lance", 1), ("Scalpel", 1), ("Ruban adhésif", 2)],
              category="Survie")
app.add_craft("Lance avec cuillère",
              [("Lance", 1), ("Cuillère", 1), ("Ruban adhésif", 2)],
              category="Survie")
app.add_craft("Lance avec ciseaux",
              [("Lance", 1), ("Ciseaux", 1), ("Ruban adhésif", 2)],
              category="Survie")
app.add_craft("Lance avec fourche à main",
              [("Lance", 1), ("Fourche à main", 1), ("Ruban adhésif", 2)],
              category="Survie")
app.add_craft("Lance avec tournevis",
              [("Lance", 1), ("Tournevis", 1), ("Ruban adhésif", 2)],
              category="Survie")

# Catégorie Menuiserie
app.add_craft("Planche", [("Bûche", 1)], category="Menuiserie")
app.add_craft("Mortier et pilon", [("Planche", 1)], category="Menuiserie")
app.add_craft("Seau de plâtre",
              [("Seau", 1), ("Eau", 5), ("Plâtre", 1)],
              category="Menuiserie")
app.add_craft("Tiroir",
              [("Planche", 1), ("Poignée de porte", 1), ("Clous", 1)],
              category="Menuiserie")
app.add_craft("Matelas",
              [("Bobine de fil", 2), ("Drap", 5), ("Coussin", 5)],
              category="Menuiserie")
app.add_craft("Pile de bûches", [("Corde", 2), ("Bûche", 2)], category="Menuiserie")
app.add_craft("Batte de baseball cloutée",
              [("Batte de baseball", 1), ("Clous", 5)],
              category="Menuiserie")
app.add_craft("Planche cloutée",
              [("Planche", 1), ("Clous", 5)],
              category="Menuiserie")
app.add_craft("Barricade en bois",
              [("Porte", 1), ("Fenêtre", 1), ("Planche", 1), ("Clous", 2)],
              category="Menuiserie")
app.add_craft("Pieu en bois", [("Planche", 1), ("Clous", 2)], category="Menuiserie")
app.add_craft("Barrière en bois", [("Fil barbelé", 1)], category="Menuiserie")
app.add_craft("Clôture en bois", [("Planche", 2), ("Clous", 3)], category="Menuiserie")
app.add_craft("Mur en sacs de sable", [("Sac de sable", 3)], category="Menuiserie")
app.add_craft("Mur en sacs de gravier", [("Sac de gravier", 3)], category="Menuiserie")
app.add_craft("Caisse en bois", [("Planche", 3), ("Clous", 3)], category="Menuiserie")
app.add_craft("Élément de bar", [("Planche", 4), ("Clous", 4)], category="Menuiserie")
app.add_craft("Angle de bar", [("Planche", 4), ("Clous", 4)], category="Menuiserie")
app.add_craft("Petite table", [("Planche", 5), ("Clous", 4)], category="Menuiserie")
app.add_craft("Grande table", [("Planche", 6), ("Clous", 4)], category="Menuiserie")
app.add_craft("Table avec tiroir", [("Planche", 5), ("Clous", 4), ("Tiroir", 1)], category="Menuiserie")
app.add_craft("Chaise en bois", [("Planche", 5), ("Clous", 4)], category="Menuiserie")
app.add_craft("Collecteur d'eau de pluie",
              [("Planche", 4), ("Clous", 4), ("Sac poubelle", 4)],
              category="Menuiserie")
app.add_craft("Composteur", [("Planche", 5), ("Clous", 4)], category="Menuiserie")
app.add_craft("Bibliothèque", [("Planche", 5), ("Clous", 4)], category="Menuiserie")
app.add_craft("Petite bibliothèque", [("Planche", 3), ("Clous", 3)], category="Menuiserie")
app.add_craft("Étagères", [("Planche", 1), ("Clous", 2)], category="Menuiserie")
app.add_craft("Double étagères", [("Planche", 2), ("Clous", 4)], category="Menuiserie")
app.add_craft("Lit", [("Planche", 6), ("Clous", 4), ("Matelas", 1)], category="Menuiserie")
app.add_craft("Cairn", [("Pierre", 6)], category="Menuiserie")
app.add_craft("Lampe sur pilier",
              [("Planche", 2), ("Clous", 4), ("Corde", 1), ("Lampe de poche", 1)],
              category="Menuiserie")
app.add_craft("Croix en bois", [("Planche", 2), ("Clous", 2)], category="Menuiserie")
app.add_craft("Piquet en bois", [("Planche", 1), ("Corde de drap", 1)], category="Menuiserie")
app.add_craft("Panneau en bois", [("Planche", 3), ("Clous", 3)], category="Menuiserie")
app.add_craft("Cadre en bois", [("Planche", 2), ("Clous", 2)], category="Menuiserie")
app.add_craft("Mur en bois", [("Planche", 2), ("Clous", 2)], category="Menuiserie")
app.add_craft("Fenêtre en bois", [("Planche", 2), ("Clous", 4)], category="Menuiserie")
app.add_craft("Châssis de porte en bois", [("Planche", 4), ("Clous", 4)], category="Menuiserie")
app.add_craft("Pilier en bois", [("Planche", 4), ("Clous", 4)], category="Menuiserie")
app.add_craft("Mur en rondins",
              [("Tissu déchiré", 4), ("Corde", 4), ("Rope", 2), ("Bûche", 4)],
              category="Menuiserie")
app.add_craft("Porte en bois",
              [("Planche", 4), ("Clous", 4), ("Charnière", 2), ("Poignée de porte", 1)],
              category="Menuiserie")
app.add_craft("Porte double en bois",
              [("Planche", 12), ("Clous", 12), ("Charnière", 4), ("Poignée de porte", 2)],
              category="Menuiserie")
app.add_craft("Escaliers", [("Planche", 15), ("Clous", 15)], category="Menuiserie")
app.add_craft("Plancher en bois", [("Planche", 1), ("Clous", 1)], category="Menuiserie")

# Catégorie Électrique
app.add_craft("Composant électronique",
              [("Téléphone sans fil", 1), ("Montre numérique", 1), ("Écouteurs", 1),
               ("Lampe de poche", 1), ("Torche à main", 1), ("Casque", 1), ("Jeu vidéo", 1)],
              category="Électrique")
app.add_craft("Composant électronique", [("Lecteur CD", 1)], category="Électrique")
app.add_craft("Capteur de mouvement", [("Alarme maison", 1)], category="Électrique")
app.add_craft("Amplificateur", [("Haut-parleur", 1)], category="Électrique")
app.add_craft("Récepteur", [("Télécommande TV", 1)], category="Électrique")
app.add_craft("Composant électronique",
              [("Radio ValuTech", 1), ("Radio Premium Technologies", 1)],
              category="Électrique")
app.add_craft("Composant électronique",
              [("Télévision antique", 1), ("Télévision ValuTech", 1), ("Télévision Premium Technologies", 1)],
              category="Électrique")
app.add_craft("Composant électronique",
              [("Radio ham Premium Technologies", 1), ("Radio ham US Army", 1)],
              category="Électrique")
app.add_craft("Déclencheur",
              [("Récepteur radio", 1), ("Récepteur", 1), ("Composant électronique", 2),
               ("Colle", 2), ("Magazine électronique Vol. 4", 1)],
              category="Électrique")
app.add_craft("Minuterie",
              [("Réveil", 1), ("Minuterie", 1), ("Composant électronique", 1),
               ("Colle", 1), ("Magazine électronique Vol. 2", 1)],
              category="Électrique")
app.add_craft("Télécommande V1",
              [("Télécommande TV", 1), ("Composant électronique", 2),
               ("Colle", 2), ("Magazine électronique Vol. 1", 1)],
              category="Électrique")
app.add_craft("Télécommande V2",
              [("Télécommande TV", 1), ("Composant électronique", 3),
               ("Colle", 2), ("Magazine électronique Vol. 1", 1)],
              category="Électrique")
app.add_craft("Télécommande V3",
              [("Télécommande TV", 1), ("Composant électronique", 4),
               ("Colle", 2), ("Magazine électronique Vol. 1", 1)],
              category="Électrique")
app.add_craft("Radio de fortune",
              [("Composant électronique", 2), ("Amplificateur", 1),
               ("Ampoule", 1), ("Récepteur radio", 1), ("Fil électrique", 1),
               ("Aluminium", 2), ("Magazine électronique Vol. 1", 1)],
              category="Électrique")
app.add_craft("Talkie-walkie de fortune",
              [("Composant électronique", 3), ("Amplificateur", 1),
               ("Ampoule", 1), ("Ampoule verte", 1), ("Transmetteur radio", 1),
               ("Fil électrique", 2), ("Aluminium", 3), ("Magazine électronique Vol. 2", 1)],
              category="Électrique")
app.add_craft("Radio de fortune",
              [("Composant électronique", 4), ("Amplificateur", 1),
               ("Ampoule", 1), ("Ampoule verte", 1), ("Transmetteur radio", 1),
               ("Fil électrique", 3), ("Aluminium", 4), ("Magazine mécanique", 1)],
              category="Électrique")

# Catégorie Ingénierie
app.add_craft("Bombe aérosol", [("Aérosol", 1), ("Cocarde", 1), ("Aluminium", 1)], category="Ingénierie")
app.add_craft("Bombe incendiaire", [("Bouteille vide", 1), ("Essence", 4), ("Tissu déchiré", 1)], category="Ingénierie")

# Bombes avec minuterie et capteurs (catégorie Électrique)
app.add_craft("Bombe aérosol avec minuterie",
              [("Bombe aérosol", 1), ("Minuterie", 1), ("Composant électronique", 2),
               ("Ruban adhésif", 1), ("Magazine électronique Vol. 2", 1)],
              category="Électrique")
app.add_craft("Bombe aérosol avec capteur (V1)",
              [("Bombe aérosol", 1), ("Capteur de mouvement", 1), ("Composant électronique", 2),
               ("Ruban adhésif", 1), ("Magazine électronique Vol. 3", 1)],
              category="Électrique")
app.add_craft("Bombe incendiaire avec minuterie",
              [("Bombe incendiaire", 1), ("Minuterie", 1), ("Composant électronique", 2),
               ("Ruban adhésif", 1), ("Magazine électronique Vol. 2", 1)],
              category="Électrique")
app.add_craft("Bombe incendiaire avec capteur (V1)",
              [("Bombe incendiaire", 1), ("Capteur de mouvement", 1), ("Composant électronique", 2),
               ("Ruban adhésif", 1), ("Magazine électronique Vol. 3", 1)],
              category="Électrique")

# Quelques ajouts supplémentaires
app.add_craft("Bâton", [("Bois", 2)], category="Survie")
app.add_craft("Couteau en pierre",
              [("Branche d’arbre", 1), ("Pierre coupante", 1), ("Ficelle", 1)],
              category="Survie")
app.add_craft("Kit pour feu de camp",
              [("Bois", 5), ("Brindilles", 10), ("Feuille", 3)],
              category="Survie")
app.add_craft("Porte",
              [("Marteau", 10), ("Planche", 4), ("Clou", 8),
               ("Charnière de porte", 2), ("Poignée de porte", 1)],
              category="Menuiserie")

# Chargement des recettes
recipes = app.load_craft_recipes()

