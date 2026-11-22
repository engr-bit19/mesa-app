import pymysql
from flask import Flask, g, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static")

# XAMPP defaults: user root, empty password
DB = dict(host="localhost", user="root", password="", database="mesa",
          cursorclass=pymysql.cursors.DictCursor, autocommit=True)


def db():
    if "db" not in g:
        g.db = pymysql.connect(**DB)
    return g.db


def query(sql, args=()):
    with db().cursor() as cur:
        cur.execute(sql, args)
        return cur.fetchall()


@app.teardown_appcontext
def close_db(_):
    conn = g.pop("db", None)
    if conn:
        conn.close()


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/api/recipes")
def recipes():
    out = []
    for r in query("SELECT * FROM recipes ORDER BY id"):
        tags = [t["name"] for t in query(
            "SELECT t.name FROM tags t JOIN recipe_tags rt ON rt.tag_id=t.id WHERE rt.recipe_id=%s", (r["id"],))]
        ings = [[i["name"], i["quantity"], i["unit"], i["category"]] for i in query(
            """SELECT i.name, i.category, ri.quantity, ri.unit
               FROM recipe_ingredients ri JOIN ingredients i ON i.id=ri.ingredient_id
               WHERE ri.recipe_id=%s""", (r["id"],))]
        out.append({"id": r["id"], "t": r["title"], "c": r["color"], "time": r["minutes"],
                    "sv": r["servings"], "tags": tags, "ing": ings})
    return jsonify(out)


@app.get("/api/plan")
def get_plan():
    rows = query("SELECT day, meal, recipe_id FROM plan_entries")
    return jsonify({f"{r['day']}|{r['meal']}": r["recipe_id"] for r in rows})


@app.put("/api/plan")
def put_plan():
    d = request.get_json()
    try:
        query("REPLACE INTO plan_entries(day, meal, recipe_id) VALUES (%s,%s,%s)",
              (d["day"], d["meal"], d["recipe_id"]))
    except (pymysql.MySQLError, KeyError):
        return jsonify({"error": "Invalid day, meal or recipe"}), 400
    return jsonify({"ok": True})


@app.delete("/api/plan/<day>/<meal>")
def delete_plan(day, meal):
    query("DELETE FROM plan_entries WHERE day=%s AND meal=%s", (day, meal))
    return jsonify({"ok": True})


@app.get("/api/shopping")
def shopping():
    people = request.args.get("people", 2, type=int)
    rows = query(
        """SELECT i.name, i.category, ri.unit,
                  SUM(ri.quantity * %s / r.servings) AS total
           FROM plan_entries p
           JOIN recipes r ON r.id = p.recipe_id
           JOIN recipe_ingredients ri ON ri.recipe_id = r.id
           JOIN ingredients i ON i.id = ri.ingredient_id
           GROUP BY i.name, i.category, ri.unit
           ORDER BY i.category, i.name""", (people,))
    return jsonify(rows)


if __name__ == "__main__":
    app.run(debug=True)