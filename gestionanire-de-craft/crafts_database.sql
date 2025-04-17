-- Création de la table Craft
CREATE TABLE IF NOT EXISTS Craft (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,  -- Empêche les doublons dans les crafts
    favorite INTEGER DEFAULT 0 -- Indique si un craft est favori (0 par défaut)
);

-- Création de la table Ingredient
CREATE TABLE IF NOT EXISTS Ingredient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE -- Empêche les doublons dans les ingrédients
);

-- Création de la table CraftIngredient pour lier les crafts aux ingrédients
CREATE TABLE IF NOT EXISTS CraftIngredient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    craft_id INTEGER NOT NULL, -- Référence à la table Craft
    ingredient_id INTEGER NOT NULL, -- Référence à la table Ingredient
    quantity INTEGER DEFAULT 1, -- Quantité d'ingrédient requise pour le craft
    FOREIGN KEY (craft_id) REFERENCES Craft(id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(id),
    UNIQUE(craft_id, ingredient_id) -- Empêche les doublons dans les associations
);

-- Ajout d'index pour optimiser les recherches
CREATE INDEX IF NOT EXISTS idx_craft_id ON CraftIngredient(craft_id);
CREATE INDEX IF NOT EXISTS idx_ingredient_id ON CraftIngredient(ingredient_id);