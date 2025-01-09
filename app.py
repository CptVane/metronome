import os
import json
from flask import Flask, redirect, url_for, flash, request
from routes import create_routes
from models import db
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_super_secret_key_here"

migrate = Migrate(app, db)

# Default settings
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

if not os.path.exists(settings_file):
    raise FileNotFoundError(f"Il file {settings_file} non esiste. Crealo prima di avviare l'app.")

with open(settings_file) as f:
    settings = json.load(f)

# Configurazione del database
# Check for the POSTGRES_URI environment variable first
database_uri = os.getenv('POSTGRES_URI')

if not database_uri:
    db_type = settings.get("db_type", "sqlite")
    if db_type == "sqlite":
        sqlite_path = settings.get("sqlite_path", "metronome.db")
        database_uri = f"sqlite:///{sqlite_path}"
    elif db_type == "postgresql":
        pg_config = settings.get("postgresql", {})
        database_uri = (
            f"postgresql://{pg_config.get('username')}:{pg_config.get('password')}@"
            f"{pg_config.get('host')}:{pg_config.get('port')}/{pg_config.get('database')}"
        )
    else:
        raise ValueError(f"Tipo di database '{db_type}' non supportato.")

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)
print(f"Connesso al database: {database_uri}")

# Register routes
create_routes(app)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
