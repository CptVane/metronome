from datetime import datetime, timedelta
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import OperationalError
from flask import current_app
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def calculate_work_time(start_time, end_time, break_time):
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)

    if end_dt < start_dt:
        end_dt += timedelta(days=1)

    duration = (end_dt - start_dt).total_seconds() / 3600  # Convert to hours
    work_time = max(duration - (break_time / 60), 0)
    return work_time

def calculate_total_fee(work_time, base_fee=230):
    if work_time <= 10:
        return base_fee
    else:
        extra_hours = work_time - 10
        return base_fee + (25 * extra_hours)

"""
def reset_database_connection(app, db, config):
    
    #Reinizializza la connessione al database con il contesto applicativo corretto.
  
    db_type = config.get("db_type", "sqlite")

    # Usa app.instance_path per calcolare il percorso assoluto del database
    if db_type == "sqlite":
        sqlite_path = os.path.join(app.instance_path, config.get("sqlite_path", "metronome.db"))
        new_uri = f"sqlite:///{sqlite_path}"
    elif db_type == "postgresql":
        pg_config = config.get("postgresql", {})
        new_uri = (
            f"postgresql://{pg_config.get('username')}:{pg_config.get('password')}@"
            f"{pg_config.get('host')}:{pg_config.get('port')}/{pg_config.get('database')}"
        )
    else:
        raise ValueError("Tipo di database non supportato.")

    print(f"Switching to database URI: {new_uri}")

    with app.app_context():
        # Aggiorna l'URI del database
        app.config['SQLALCHEMY_DATABASE_URI'] = new_uri

        # Elimina sessioni e motore precedenti
        try:
            db.session.remove()
            db.engine.dispose()
            print("Vecchio motore smaltito.")
        except Exception as e:
            print(f"Errore durante la rimozione del motore precedente: {e}")

        # Verifica la connessione senza creare tabelle
        try:
            new_engine = create_engine(new_uri, echo=True)
            with new_engine.connect() as connection:
                connection.execute(text("SELECT 1"))  # Verifica la connessione
                print("Connessione al database verificata.")
            # Reimposta il contesto di SQLAlchemy
            db.session = scoped_session(sessionmaker(bind=new_engine))
            db.metadata.bind = new_engine
            db.init_app(app)  # Associa SQLAlchemy all'app corrente
        except OperationalError as e:
            print(f"Errore durante la connessione al database: {e}")
            raise RuntimeError("Connessione al database fallita.")



def verify_essential_tables(app, db):

    #Verifica che le tabelle essenziali siano presenti nel database.

    with app.app_context():
        inspector = inspect(db.engine)  # Utilizza il motore configurato
        tables = inspector.get_table_names()
        if 'workday' not in tables:
            raise RuntimeError("Tabella 'workday' non trovata. Database non valido.")
        print(f"Tabelle presenti nel database: {tables}")
"""