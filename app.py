import os
import json
from flask import Flask, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from routes import create_routes
from helpers import reset_database_connection
from models import db

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_super_secret_key_here"

# Impostazioni predefinite
default_settings = {
    "db_type": "sqlite",
    "sqlite_path": "metronome.db",
    "postgresql": {
        "username": "metronome_user",
        "password": "secure_password",
        "host": "localhost",
        "port": "5432",
        "database": "metronome"
    },
    "username": "Admin",
    "password": "password123",
    "name": "Admin",
    "lastname": "User",
    "email": "admin@example.com",
    "phone": "1234567890",
    "base_fee": 230.0
}

settings_file = 'settings.json'
emergency_mode = True

# Carica le impostazioni
if not os.path.exists(settings_file):
    with open(settings_file, 'w') as f:
        json.dump(default_settings, f, indent=4)
    settings = default_settings
else:
    try:
        with open(settings_file) as f:
            settings = json.load(f)
    except json.JSONDecodeError:
        with open(settings_file, 'w') as f:
            json.dump(default_settings, f, indent=4)
        settings = default_settings

# Connessione al database
try:
    with app.app_context():
        reset_database_connection(app, db, settings)
    emergency_mode = False
    print("Database connection established.")
except RuntimeError as e:
    print(f"Database connection failed: {e}")
    emergency_mode = True

# Middleware per reindirizzare in modalità d'emergenza
@app.before_request
def handle_emergency_mode():
    global emergency_mode
    if emergency_mode and request.endpoint != 'settings':
        flash("Database connection failed. Update settings.", "danger")
        return redirect(url_for('settings'))

# Registra le rotte
create_routes(app)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)