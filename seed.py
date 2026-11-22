"""Creates the MySQL database 'mesa', its tables, and sample recipes.
Needs XAMPP's MySQL running. Run once: python seed.py"""
import pymysql

HOST, USER, PASSWORD = "localhost", "root", ""   # XAMPP defaults

CATEGORY = {"Chicken thighs": "Meat", "Pork belly": "Meat", "Egg": "Dairy & eggs",
            "Soy sauce": "Pantry", "Vinegar": "Pantry", "Tamarind mix": "Pantry",
            "Cooking oil": "Pantry", "Rice": "Pantry", "Canton noodles": "Pantry",
            "Bay leaves": "Pantry"}

RECIPES = [
 ("Chicken adobo", "#8a4b2d", 55, 4, ["chicken", "rice meal"],
  [("Chicken thighs", 800, "g"), ("Soy sauce", 60, "ml"), ("Vinegar", 60, "ml"), ("Garlic", 6, "cloves"), ("Bay leaves", 3, "pcs")]),
 ("Sinigang na baboy", "#4d7a3a", 70, 4, ["pork", "soup"],
  [("Pork belly", 600, "g"), ("Tamarind mix", 1, "pack"), ("Kangkong", 1, "bunch"), ("Tomato", 2, "pcs"), ("Onion", 1, "pcs")]),
 ("Tortang talong", "#6b4c8a", 20, 2, ["vegetarian", "under 30 min"],
  [("Eggplant", 3, "pcs"), ("Egg", 3, "pcs"), ("Onion", 1, "pcs"), ("Cooking oil", 30, "ml")]),
 ("Arroz caldo", "#b5832a", 45, 4, ["chicken", "soup"],
  [("Chicken thighs", 500, "g"), ("Rice", 200, "g"), ("Garlic", 5, "cloves"), ("Ginger", 30, "g"), ("Egg", 2, "pcs")]),
 ("Garlic rice & egg", "#2f6f86", 15, 2, ["vegetarian", "under 30 min", "rice meal"],
  [("Rice", 300, "g"), ("Garlic", 4, "cloves"), ("Egg", 2, "pcs"), ("Cooking oil", 20, "ml")]),
 ("Pancit canton", "#a8453a", 30, 4, ["pork", "noodles"],
  [("Canton noodles", 250, "g"), ("Pork belly", 200, "g"), ("Carrot", 1, "pcs"), ("Onion", 1, "pcs"), ("Soy sauce", 30, "ml")]),
]

SCHEMA = [
 "DROP TABLE IF EXISTS plan_entries",
 "DROP TABLE IF EXISTS recipe_tags",
 "DROP TABLE IF EXISTS recipe_ingredients",
 "DROP TABLE IF EXISTS tags",
 "DROP TABLE IF EXISTS ingredients",
 "DROP TABLE IF EXISTS recipes",
 """CREATE TABLE recipes (
      id INT AUTO_INCREMENT PRIMARY KEY,
      title VARCHAR(100) NOT NULL,
      color VARCHAR(7) NOT NULL DEFAULT '#1f4d43',
      minutes INT NOT NULL,
      servings INT NOT NULL)""",
 """CREATE TABLE ingredients (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(100) NOT NULL UNIQUE,
      category VARCHAR(50) NOT NULL DEFAULT 'Produce')""",
 """CREATE TABLE recipe_ingredients (
      recipe_id INT NOT NULL,
      ingredient_id INT NOT NULL,
      quantity DOUBLE NOT NULL,
      unit VARCHAR(20) NOT NULL,
      PRIMARY KEY (recipe_id, ingredient_id),
      FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
      FOREIGN KEY (ingredient_id) REFERENCES ingredients(id))""",
 """CREATE TABLE tags (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(50) NOT NULL UNIQUE)""",
 """CREATE TABLE recipe_tags (
      recipe_id INT NOT NULL,
      tag_id INT NOT NULL,
      PRIMARY KEY (recipe_id, tag_id),
      FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
      FOREIGN KEY (tag_id) REFERENCES tags(id))""",
 """CREATE TABLE plan_entries (
      day ENUM('Mon','Tue','Wed','Thu','Fri','Sat','Sun') NOT NULL,
      meal ENUM('Breakfast','Lunch','Dinner') NOT NULL,
      recipe_id INT NOT NULL,
      PRIMARY KEY (day, meal),
      FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE)""",
]

con = pymysql.connect(host=HOST, user=USER, password=PASSWORD)
cur = con.cursor()
cur.execute("CREATE DATABASE IF NOT EXISTS mesa CHARACTER SET utf8mb4")
cur.execute("USE mesa")
for stmt in SCHEMA:
    cur.execute(stmt)

for title, color, mins, serv, tags, ings in RECIPES:
    cur.execute("INSERT INTO recipes(title,color,minutes,servings) VALUES (%s,%s,%s,%s)",
                (title, color, mins, serv))
    rid = cur.lastrowid
    for t in tags:
        cur.execute("INSERT IGNORE INTO tags(name) VALUES (%s)", (t,))
        cur.execute("SELECT id FROM tags WHERE name=%s", (t,))
        cur.execute("INSERT INTO recipe_tags VALUES (%s,%s)", (rid, cur.fetchone()[0]))
    for name, qty, unit in ings:
        cur.execute("INSERT IGNORE INTO ingredients(name,category) VALUES (%s,%s)",
                    (name, CATEGORY.get(name, "Produce")))
        cur.execute("SELECT id FROM ingredients WHERE name=%s", (name,))
        cur.execute("INSERT INTO recipe_ingredients VALUES (%s,%s,%s,%s)",
                    (rid, cur.fetchone()[0], qty, unit))

con.commit()
con.close()
print("Created MySQL database 'mesa' with", len(RECIPES), "recipes")