from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "shortech2025")
DATABASE = "database.db"

# Crée la table si elle n'existe pas
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

# ... le reste du code reste inchangé ...

# Admin : afficher les inscrits et formulaire de connexion
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

    # GET => juste la page login admin
    return render_template("admin.html", access_granted=False)

# Admin : afficher les inscrits
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
