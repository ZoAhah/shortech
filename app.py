from flask import Flask, render_template, request, redirect, session, url_for, send_file
import csv
import os
import re
import datetime

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète_ici'  # à personnaliser en production

DATA_FILE = 'data/leads.csv'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'shorttech2025'

def email_exists(email):
    if not os.path.exists(DATA_FILE):
        return False
    with open(DATA_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 1 and row[1].lower() == email.lower():
                return True
    return False

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

@app.route('/')
def index():
    return render_template('index.html', message=None)

@app.route('/submit', methods=['POST'])
def submit():
    firstname = request.form.get('firstname', '').strip()
    email = request.form.get('email', '').strip()
    job = request.form.get('job', '').strip()
    location = request.form.get('location', '').strip()
    contract = request.form.get('contract', '').strip()

    if not firstname or not email or not job or not location or not contract:
        return render_template('index.html', message="Tous les champs sont obligatoires.", success=False)

    if not is_valid_email(email):
        return render_template('index.html', message="Email invalide.", success=False)

    if email_exists(email):
        return render_template('index.html', message="Cet email est déjà inscrit.", success=False)

    os.makedirs('data', exist_ok=True)
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        writer.writerow([firstname, email, job, location, contract, date_now])

    return render_template('index.html', message="Merci ! Tu recevras bientôt des offres 👍", success=True)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Identifiants incorrects.")
    return render_template('admin_login.html')

@app.route('/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    filters = {
        'firstname': request.args.get('firstname', '').lower(),
        'email': request.args.get('email', '').lower(),
        'job': request.args.get('job', '').lower(),
        'location': request.args.get('location', '').lower(),
        'contract': request.args.get('contract', '').lower()
    }

    data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 6:
                    continue
                match = True
                if filters['firstname'] and filters['firstname'] not in row[0].lower():
                    match = False
                if filters['email'] and filters['email'] not in row[1].lower():
                    match = False
                if filters['job'] and filters['job'] not in row[2].lower():
                    match = False
                if filters['location'] and filters['location'] not in row[3].lower():
                    match = False
                if filters['contract'] and filters['contract'] != row[4].lower():
                    match = False
                if match:
                    data.append(row)

    return render_template('admin_dashboard.html', data=data)

@app.route('/download')
def download_csv():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    if os.path.exists(DATA_FILE):
        return send_file(DATA_FILE, as_attachment=True)
    return "Fichier introuvable", 404

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
