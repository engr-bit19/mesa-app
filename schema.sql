PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS recipes (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  title     TEXT NOT NULL,
  color     TEXT NOT NULL DEFAULT '#1f4d43',
  minutes   INTEGER NOT NULL,
  servings  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS ingredients (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  name      TEXT NOT NULL UNIQUE,
  category  TEXT NOT NULL DEFAULT 'Produce'
);

-- junction: recipes <-> ingredients (many-to-many)
CREATE TABLE IF NOT EXISTS recipe_ingredients (
  recipe_id     INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
  quantity      REAL NOT NULL,
  unit          TEXT NOT NULL,
  PRIMARY KEY (recipe_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS tags (
  id   INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS recipe_tags (
  recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  tag_id    INTEGER NOT NULL REFERENCES tags(id),
  PRIMARY KEY (recipe_id, tag_id)
);

-- one row per slot in the week; PRIMARY KEY means a slot holds one recipe
CREATE TABLE IF NOT EXISTS plan_entries (
  day       TEXT NOT NULL CHECK (day IN ('Mon','Tue','Wed','Thu','Fri','Sat','Sun')),
  meal      TEXT NOT NULL CHECK (meal IN ('Breakfast','Lunch','Dinner')),
  recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  PRIMARY KEY (day, meal)
);
