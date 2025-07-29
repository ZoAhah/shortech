from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "shortech2025")
DATABASE = "database.db"

# ✅ Crée la table si elle n'existe pas
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS candidates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        location TEXT NOT NULL,
                        position TEXT NOT NULL,
                        contract_type TEXT NOT NULL,
                        date TEXT NOT NULL
                    )''')
        conn.commit()

init_db()

# ✅ Page principale
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        location = request.form["location"]
        position = request.form["position"]
        contract_type = request.form["contract_type"]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not all([name, email, location, position, contract_type]):
            flash("Tous les champs sont obligatoires.")
            return redirect(url_for("index"))

        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO candidates (name, email, location, position, contract_type, date) VALUES (?, ?, ?, ?, ?, ?)",
                      (name, email, location, position, contract_type, date))
            conn.commit()

        flash("Inscription enregistrée avec succès ✅")
        return redirect(url_for("index"))

    return render_template("index.html")

# ✅ Admin : afficher les inscrits
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password != ADMIN_PASSWORD:
            flash("Mot de passe incorrect ❌")
            return redirect(url_for("admin"))

        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM candidates ORDER BY date DESC")
            rows = c.fetchall()

        return render_template("admin.html", rows=rows, access_granted=True)

    return render_template("admin.html", access_granted=False)

if __name__ == "__main__":
    app.run(debug=True)
