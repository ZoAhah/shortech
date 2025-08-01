import os
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- Configuration email (avec Flask-Mail) ---
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.environ.get("MAIL_DEFAULT_SENDER")
)
mail = Mail(app)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "shortech2025")
DATABASE = "database.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS candidates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, email TEXT, location TEXT,
                        position TEXT, contract_type TEXT, date TEXT)''')
init_db()

def scraper_hellowork(position, location):
    q = position.replace(" ", "+")
    l = location.replace(" ", "+")
    url = f"https://www.hellowork.com/fr-fr/emploi/recherche.html?k={q}&l={l}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    offers = []
    for job in soup.select(".job-card"):
        title = job.select_one(".job-card__title")
        loc = job.select_one(".job-card__location")
        link = job.select_one("a")
        ct = job.select_one(".job-card__contract .contract-type")
        if title and link and loc:
            offers.append({
                "title": title.text.strip(),
                "location": loc.text.strip(),
                "contract": ct.text.strip() if ct else "",
                "link": "https://www.hellowork.com" + link["href"]
            })
        if len(offers) >= 5:
            break
    return offers

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        firstname = request.form["firstname"]
        email = request.form["email"]
        location = request.form["location"]
        position = request.form["job"]
        contract = request.form["contract"]
        date = datetime.now().strftime("%Y‑%m‑%d %H:%M")

        if not all([firstname, email, location, position, contract]):
            flash("Tous les champs sont obligatoires.", "error")
            return redirect(url_for("index"))

        with sqlite3.connect(DATABASE) as conn:
            conn.execute(
                "INSERT INTO candidates (name,email,location,position,contract_type,date) VALUES (?,?,?,?,?,?)",
                (firstname, email, location, position, contract, date)
            )
            conn.commit()

        offers = scraper_hellowork(position, location)
        # Envoi d'email
        subject = f"ShortTech – Offres pour {position}"
        html_body = render_template("email_offers.html", firstname=firstname, offers=offers)
        msg = Message(subject, recipients=[email], html=html_body)
        mail.send(msg)

        flash("Inscription réussie ! Les offres arrivent bientôt par mail ✅", "success")
        return redirect(url_for("index"))
    return render_template("index.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") != ADMIN_PASSWORD:
            flash("Mot de passe incorrect", "error")
            return redirect(url_for("admin"))
        with sqlite3.connect(DATABASE) as conn:
            rows = conn.execute("SELECT * FROM candidates ORDER BY date DESC").fetchall()
        return render_template("admin.html", access_granted=True, rows=rows)
    return render_template("admin.html", access_granted=False)

if __name__ == "__main__":
    app.run(debug=True)
