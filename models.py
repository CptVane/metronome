from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

# Models
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_id = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = db.relationship('Client', backref=db.backref('events', lazy=True))

'''
class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=db.backref('works', lazy=True))
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    break_time = db.Column(db.Integer, default=0)  # Break time in minutes
    work_time = db.Column(db.Float, nullable=False)  # Work time in hours
    fee = db.Column(db.Float, nullable=False)
    total_fee = db.Column(db.Float, nullable=False)
    
'''

class Workday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)  # Linked to Event
    event = db.relationship('Event', backref=db.backref('workdays', lazy=True))  # Add this line
    date = db.Column(db.Date, nullable=False)  # Workday Date
    start_time = db.Column(db.Time, nullable=False)  # Start Time
    end_time = db.Column(db.Time, nullable=False)  # End Time
    break_time = db.Column(db.Integer, nullable=False, default=0)  # Break Time in minutes
    work_time = db.Column(db.Float, nullable=False)  # Work Time in hours
    fee = db.Column(db.Float, nullable=False)  # Daily Fee
    total_fee = db.Column(db.Float, nullable=False)  # Total Fee (work_time * fee)
    
    use_overriden_fee = db.Column(db.Boolean, nullable=False, default=False)  # Usa Tariffa Manuale
    override_fee = db.Column(db.Float, nullable=False, default=0.0)  # Tariffa Manuale
    highlighted = db.Column(db.Boolean, nullable=False, default=False)  # Evidenziato
    tags = db.Column(JSON, nullable=True)
