from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.orm import joinedload
from models import db, Client, Event, Workday
from helpers import calculate_work_time, calculate_total_fee
from datetime import datetime


def create_routes(app):
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

        # Query with joinedload to include related 'event' objects
        workdays = Workday.query.options(joinedload(Workday.event)).filter(
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

    @app.route('/edit_workday/<int:workday_id>', methods=['GET', 'POST'])
    def edit_workday(workday_id):
        workday = Workday.query.get_or_404(workday_id)

        if request.method == 'POST':
            # Parse date and time fields
            workday.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()

            # Handle time fields with seconds
            start_time = request.form['start_time']
            end_time = request.form['end_time']

            # Parse time fields
            workday.start_time = datetime.strptime(start_time,
                                                   '%H:%M:%S').time() if ':' in start_time else datetime.strptime(
                start_time, '%H:%M').time()
            workday.end_time = datetime.strptime(end_time, '%H:%M:%S').time() if ':' in end_time else datetime.strptime(
                end_time, '%H:%M').time()

            # Parse other fields
            workday.break_time = int(request.form['break_time'])
            workday.fee = float(request.form['fee'])

            # Recalculate work_time and total_fee
            workday.work_time = calculate_work_time(workday.start_time, workday.end_time, workday.break_time)
            workday.total_fee = calculate_total_fee(workday.work_time, workday.fee)

            # Commit changes
            db.session.commit()

            return redirect(url_for('dashboard'))

        # Render edit form with current workday data
        return render_template('edit_workday.html', workday=workday)

    @app.route('/duplicate_workday/<int:workday_id>', methods=['POST'])
    def duplicate_workday(workday_id):
        # Get the existing workday
        workday = Workday.query.get_or_404(workday_id)

        # Create a new workday with the same data
        new_workday = Workday(
            event_id=workday.event_id,
            date=workday.date,
            start_time=workday.start_time,
            end_time=workday.end_time,
            break_time=workday.break_time,
            work_time=workday.work_time,
            fee=workday.fee,
            total_fee=workday.total_fee,
        )

        # Add and commit the new workday
        db.session.add(new_workday)
        db.session.commit()

        return redirect(url_for('dashboard'))

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


