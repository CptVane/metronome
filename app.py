from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from flask import request
import os
import logging

logging.basicConfig(level=logging.DEBUG)

print(f"Working directory: {os.getcwd()}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metronome.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

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

class Workday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)  # Linked to Event
    date = db.Column(db.Date, nullable=False)  # Workday Date
    start_time = db.Column(db.Time, nullable=False)  # Start Time
    end_time = db.Column(db.Time, nullable=False)  # End Time
    break_time = db.Column(db.Integer, nullable=False, default=0)  # Break Time in minutes
    work_time = db.Column(db.Float, nullable=False)  # Work Time in hours
    fee = db.Column(db.Float, nullable=False)  # Daily Fee
    total_fee = db.Column(db.Float, nullable=False)  # Total Fee (work_time * fee)

    # Relationship to Event
    event = db.relationship('Event', backref=db.backref('workdays', lazy=True))

# Helpers
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

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/', methods=['GET'])
def dashboard():
    from datetime import datetime

    # Retrieve start_date and end_date from query parameters or use defaults
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Default to the first day of the current month and today if not provided
    if not start_date:
        start_date = datetime(datetime.now().year, datetime.now().month, 1).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    if not end_date:
        end_date = datetime.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Query the database for workdays within the date range and order by date
    workdays = Workday.query.filter(
        Workday.date >= start_date, Workday.date <= end_date
    ).order_by(Workday.date.asc()).all()

    # Format work_time for each workday
    for workday in workdays:
        hours = int(workday.work_time)
        minutes = int((workday.work_time - hours) * 60)
        workday.formatted_work_time = f"{hours:02}:{minutes:02}"

    return render_template(
        'dashboard.html',
        workdays=workdays,
        start_date=start_date,
        end_date=end_date
    )



@app.route('/workday_row_template')
def workday_row_template():
    next_date = request.args.get('next_date', None)
    if not next_date:
        return "Invalid date", 400
    return render_template('workday_row.html', next_date=next_date)


@app.route('/edit_workday/<int:workday_id>', methods=['GET'])
def edit_workday(workday_id):
    workday = Workday.query.get(workday_id)
    if not workday:
        return "Workday not found", 404
    return render_template('edit_workday.html', workday=workday)

@app.route('/duplicate_workday/<int:workday_id>', methods=['POST'])
def duplicate_workday(workday_id):
    workday = Workday.query.get(workday_id)
    if not workday:
        return "Workday not found", 404

    new_workday = Workday(
        date=workday.date,
        work_name=workday.work_name,
        client_name=workday.client_name,
        start_time=workday.start_time,
        end_time=workday.end_time,
        break_time=workday.break_time,
        work_time=workday.work_time,
        total_fee=workday.total_fee
    )
    db.session.add(new_workday)
    db.session.commit()
    return redirect('/')

@app.route('/delete_workday/<int:workday_id>', methods=['POST'])
def delete_workday(workday_id):
    workday = Workday.query.get(workday_id)
    if not workday:
        return "Workday not found", 404

    db.session.delete(workday)
    db.session.commit()
    return redirect('/')



@app.route('/add_work', methods=['GET', 'POST'])
def add_work():
    if request.method == 'POST':
        try:
            print("Form Data Received:", request.form)
            # Extract client information
            client_id = request.form.get('client_id')
            client_name = request.form.get('client_name')
            if not client_id and client_name:  # Create a new client if no existing client is selected
                new_client = Client(name=client_name, color=request.form.get('client_color', '#000000'))
                db.session.add(new_client)
                db.session.commit()
                client_id = new_client.id

            # Extract event information
            work_id = request.form.get('work_id')
            event_name = request.form.get('event_name')
            new_event = Event(work_id=work_id, name=event_name, client_id=client_id)
            db.session.add(new_event)
            db.session.commit()

            # Extract and save workdays
            for i in range(len(request.form.getlist('workday_date'))):
                # Workday details from the form
                date = request.form.getlist('workday_date')[i]
                start_time = datetime.strptime(request.form.getlist('workday_start_time')[i], '%H:%M').time()
                end_time = datetime.strptime(request.form.getlist('workday_end_time')[i], '%H:%M').time()
                break_time = int(request.form.getlist('workday_break_time')[i])
                daily_fee = float(request.form.getlist('workday_daily_fee')[i])

                # Calculate work_time and total_fee
                work_time = calculate_work_time(start_time, end_time, break_time)
                total_fee = calculate_total_fee(work_time, daily_fee)

                # Create new Workday entry
                new_workday = Workday(
                    event_id=new_event.id,
                    date=datetime.strptime(date, '%Y-%m-%d').date(),
                    start_time=start_time,
                    end_time=end_time,
                    break_time=break_time,
                    work_time=work_time,
                    fee=daily_fee,
                    total_fee=total_fee
                )
                db.session.add(new_workday)

            # Commit all changes
            db.session.commit()

            # Redirect to dashboard after saving
            return redirect(url_for('dashboard'))

        except Exception as e:
            print("Error:", e)
            db.session.rollback()
            return "An error occurred while adding the work.", 500

    # For GET requests, render the add_work form
    date_today = datetime.now().strftime('%Y-%m-%d')
    clients = Client.query.all()
    return render_template('add_work.html', clients=clients, date_today=date_today)