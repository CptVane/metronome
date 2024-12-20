from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metronome.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), nullable=False)  # Hex color code

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_id = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = db.relationship('Client', backref=db.backref('events', lazy=True))

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

# Calculate work time dynamically based on start_time, end_time, and break_time
def calculate_work_time(start_time, end_time, break_time):
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)

    if end_dt < start_dt:
        end_dt += timedelta(days=1)  # Assume end time is on the next day

    duration = (end_dt - start_dt).total_seconds() / 3600  # Convert to hours
    work_time = max(duration - (break_time / 60), 0)
    return work_time

@app.route('/')
def dashboard():
    start_date = request.args.get('start_date', datetime.today().replace(day=1).date())
    end_date = request.args.get('end_date', datetime.today().date())
    
    works = Work.query.filter(Work.date.between(start_date, end_date)).all()
    return render_template('dashboard.html', works=works, start_date=start_date, end_date=end_date)

@app.route('/add_work', methods=['GET', 'POST'])
def add_work():
    events = Event.query.all()  # Fetch all events for dropdown

    # Default values
    selected_event = None

    if request.method == 'POST':
        # Handle event updates or work submission
        if 'update_event' in request.form:  # Event update action
            event_id = request.form['event_id']
            selected_event = Event.query.get(event_id)
            selected_event.name = request.form['event_name']
            selected_event.work_id = request.form['work_id']
            db.session.commit()
        else:  # Add Work action
            event_id = request.form['event_id']
            date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
            end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
            break_time = int(request.form.get('break_time', 0))
            fee = float(request.form['fee'])

            # Calculate work_time and total_fee
            start_dt = datetime.combine(date, start_time)
            end_dt = datetime.combine(date, end_time)
            if end_dt < start_dt:
                end_dt += timedelta(days=1)

            work_time = max((end_dt - start_dt).total_seconds() / 3600 - (break_time / 60), 0)
            total_fee = work_time * fee

            work = Work(
                event_id=event_id,
                date=date,
                start_time=start_time,
                end_time=end_time,
                break_time=break_time,
                work_time=work_time,
                fee=fee,
                total_fee=total_fee
            )
            db.session.add(work)
            db.session.commit()
            return redirect(url_for('dashboard'))

    # Render page with optional selected event
    selected_event_id = request.args.get('event_id', None)
    if selected_event_id:
        selected_event = Event.query.get(selected_event_id)

    return render_template('add_work.html', events=events, selected_event=selected_event)


@app.route('/manage_clients', methods=['GET', 'POST'])
def manage_clients():
    if request.method == 'POST':
        if 'create_client' in request.form:
            name = request.form['name']
            color = request.form['color']
            new_client = Client(name=name, color=color)
            db.session.add(new_client)
            db.session.commit()
        elif 'edit_client' in request.form:
            client_id = request.form['client_id']
            client = Client.query.get(client_id)
            client.name = request.form['name']
            client.color = request.form['color']
            db.session.commit()
        elif 'delete_client' in request.form:
            client_id = request.form['client_id']
            Client.query.filter_by(id=client_id).delete()
            db.session.commit()
    clients = Client.query.all()
    return render_template('manage_clients.html', clients=clients)


@app.route('/manage_events', methods=['GET', 'POST'])
def manage_events():
    if request.method == 'POST':
        # Handle create, edit, or duplicate
        if 'create_event' in request.form:
            work_id = request.form['work_id']
            name = request.form['name']
            client_id = request.form['client_id']
            new_event = Event(work_id=work_id, name=name, client_id=client_id)
            db.session.add(new_event)
            db.session.commit()
        elif 'edit_event' in request.form:
            event_id = request.form['event_id']
            event = Event.query.get(event_id)
            event.work_id = request.form['work_id']
            event.name = request.form['name']
            event.client_id = request.form['client_id']
            db.session.commit()
        elif 'delete_event' in request.form:
            event_id = request.form['event_id']
            Event.query.filter_by(id=event_id).delete()
            db.session.commit()
        elif 'duplicate_event' in request.form:
            event_id = request.form['event_id']
            event = Event.query.get(event_id)
            duplicated_event = Event(work_id=event.work_id + "_copy", name=event.name, client_id=event.client_id)
            db.session.add(duplicated_event)
            db.session.commit()
    events = Event.query.all()
    clients = Client.query.all()
    return render_template('manage_events.html', events=events, clients=clients)


@app.route('/global_settings')
def global_settings():
    return render_template('global_settings.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)