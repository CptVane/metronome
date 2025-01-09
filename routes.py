from flask import Flask, render_template, request, redirect, url_for, Response, flash, jsonify, session
from sqlalchemy.orm import joinedload
from models import db, Client, Event, Workday
from helpers import calculate_work_time, calculate_total_fee
from datetime import datetime
from openpyxl import Workbook
from io import BytesIO
import os, json


def create_routes(app):

    settings_file = 'settings.json'

    @app.route('/', methods=['GET'])
    def dashboard():
        from datetime import datetime

        try:

            # Initialize session dates if not set
            if 'start_date' not in session:
                session['start_date'] = datetime(datetime.now().year, datetime.now().month, 1).strftime('%Y-%m-%d')
            if 'end_date' not in session:
                session['end_date'] = datetime.now().strftime('%Y-%m-%d')

            # Get the date range from session
            start_date = session['start_date']
            end_date = session['end_date']

            # Query the database for workdays in the date range
            workdays = Workday.query.options(joinedload(Workday.event)).filter(
                Workday.date >= start_date, Workday.date <= end_date
            ).order_by(Workday.date.asc()).all()

            # Format work_time for display
            for workday in workdays:
                hours = int(workday.work_time)
                minutes = int((workday.work_time - hours) * 60)
                workday.formatted_work_time = f"{hours:02}:{minutes:02}"

            # Render the dashboard
            return render_template(
                'dashboard.html',
                workdays=workdays,
                start_date=start_date,
                end_date=end_date
            )

        except Exception as e:
            print(f"Error accessing dashboard: {e}")
            flash("Error loading dashboard. Defaulting to the current month.", "danger")
            session['start_date'] = datetime(datetime.now().year, datetime.now().month, 1).strftime('%Y-%m-%d')
            session['end_date'] = datetime.now().strftime('%Y-%m-%d')
            return redirect(url_for('dashboard'))

    @app.route('/update_date_range', methods=['POST'])
    def update_date_range():
        try:
            data = request.get_json()
            start_date = data.get('start_date')
            end_date = data.get('end_date')

            # Validate and update session
            from datetime import datetime
            datetime.strptime(start_date, '%Y-%m-%d')  # Validate format
            datetime.strptime(end_date, '%Y-%m-%d')  # Validate format

            session['start_date'] = start_date
            session['end_date'] = end_date

            return {"success": True}, 200
        except Exception as e:
            print(f"Error updating date range: {e}")
            return {"success": False, "error": str(e)}, 400

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

    @app.route('/duplicate_workday/<int:id>', methods=['POST'])
    def duplicate_workday(id):
        try:
            # Get the workday to duplicate
            original_workday = Workday.query.get_or_404(id)

            # Create a duplicate workday object
            duplicate_workday = Workday(
                date=original_workday.date,
                start_time=original_workday.start_time,
                end_time=original_workday.end_time,
                break_time=original_workday.break_time,
                work_time=original_workday.work_time,
                fee=original_workday.fee,
                total_fee=original_workday.total_fee,
                use_overriden_fee=original_workday.use_overriden_fee,
                override_fee=original_workday.override_fee,
                highlighted=False,  # By default, the duplicate should not be highlighted
                tags=original_workday.tags,
                event_id=original_workday.event_id
            )

            # Add the duplicate to the database
            db.session.add(duplicate_workday)
            db.session.commit()

            flash("Workday duplicated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error duplicating workday: {e}", "danger")

        # Redirect back to the dashboard
        return redirect(url_for('dashboard'))

    @app.route('/delete_workday/<int:id>', methods=['POST'])
    def delete_workday(id):
        try:
            # Get the date range from session
            start_date = session.get('start_date')
            end_date = session.get('end_date')

            # Fetch the workday to delete
            workday = Workday.query.get_or_404(id)
            db.session.delete(workday)
            db.session.commit()

            flash("Workday entry deleted successfully.", "success")
        except Exception as e:
            flash(f"Error deleting workday: {e}", "danger")
            db.session.rollback()

        # Redirect back to the dashboard with the same date range
        return redirect(url_for('dashboard'))

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

    @app.route('/clients')
    def clients():
        clients = Client.query.order_by(Client.name.asc()).all()
        return render_template('clients.html', clients=clients)

    @app.route('/add_client', methods=['GET', 'POST'])
    def add_client():
        if request.method == 'POST':
            name = request.form['name']
            color = request.form['color']
            new_client = Client(name=name, color=color)
            db.session.add(new_client)
            db.session.commit()
            flash('Client added successfully!', 'success')
            return redirect(url_for('clients'))
        return render_template('add_client.html')  # Crea un form HTML separato se necessario

    @app.route('/save_client', methods=['POST'])
    def save_client():
        data = request.get_json()
        client_id = data.get('id')
        name = data.get('name')
        color = data.get('color')

        client = Client.query.get_or_404(client_id)
        try:
            client.name = name
            client.color = color
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)})

    # @app.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
    # def edit_client(client_id):
    #     client = Client.query.get_or_404(client_id)
    #     if request.method == 'POST':
    #         client.name = request.form['name']
    #         client.color = request.form['color']
    #         db.session.commit()
    #         flash('Client updated successfully!', 'success')
    #         return redirect(url_for('clients'))
    #     return render_template('edit_client.html', client=client)

    @app.route('/delete_client', methods=['DELETE'])
    def delete_client():
        client_id = request.args.get('client_id', type=int)
        client = Client.query.get_or_404(client_id)
        try:
            db.session.delete(client)
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)})

    @app.route('/export_dashboard', methods=['GET'])
    def export_dashboard():
        # Fetch workdays from the database
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date:
            start_date = datetime(datetime.now().year, datetime.now().month, 1).date()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        if not end_date:
            end_date = datetime.now().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        workdays = Workday.query.filter(
            Workday.date >= start_date, Workday.date <= end_date
        ).order_by(Workday.date.asc()).all()

        # Create an Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Workdays"

        # Add header row with DETTAGLIO and DOVUTO
        ws.append(["DETTAGLIO", "DOVUTO"])

        # Populate the rows with workday data
        total_fees = 0
        for workday in workdays:
            details = f"{workday.date.strftime('%d/%m/%Y')} - {workday.event.work_id} - {workday.event.client.name} - {workday.event.name} - Ore: {int(workday.work_time)}:{int((workday.work_time - int(workday.work_time)) * 60):02}"
            fee = round(workday.total_fee, 2)
            total_fees += fee
            ws.append([details, f"€ {fee:.2f}"])

        # Add an empty row after the last entry
        ws.append([])

        # Add total row
        ws.append(["TOTAL", f"€ {total_fees:.2f}"])

        # Save the workbook to a BytesIO stream
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        # Format the filename dynamically
        filename = f"MetronomeExport_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"

        # Send the file as a response
        response = Response(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    @app.route('/toggle_highlight/<int:id>', methods=['POST'])
    def toggle_highlight(id):
        try:
            workday = Workday.query.get_or_404(id)

            # Toggle the highlighted value
            workday.highlighted = not workday.highlighted
            db.session.commit()

            return {"status": "success", "highlighted": workday.highlighted}, 200
        except Exception as e:
            db.session.rollback()
            print(f"Error toggling highlight: {e}")
            return {"status": "error", "message": str(e)}, 500

    @app.route('/settings', methods=['GET', 'POST'])
    def settings():
        if request.method == 'POST':
            # Raccogli i dati dal form
            db_type = request.form.get('db_type', 'sqlite')
            sqlite_path = request.form.get('sqlite_path', 'metronome.db')
            pg_username = request.form.get('pg_username', '')
            pg_password = request.form.get('pg_password', '')
            pg_host = request.form.get('pg_host', 'localhost')
            pg_port = request.form.get('pg_port', '5432')
            pg_database = request.form.get('pg_database', '')

            username = request.form.get('username', 'Admin')
            password = request.form.get('password', '')
            name = request.form.get('name', '')
            lastname = request.form.get('lastname', '')
            email = request.form.get('email', '')
            phone = request.form.get('phone', '')
            base_fee = float(request.form.get('base_fee', 230.0))

            # Salva le impostazioni nel file JSON
            config = {
                "db_type": db_type,
                "sqlite_path": sqlite_path,
                "postgresql": {
                    "username": pg_username,
                    "password": pg_password,
                    "host": pg_host,
                    "port": pg_port,
                    "database": pg_database
                },
                "username": username,
                "password": password,
                "name": name,
                "lastname": lastname,
                "email": email,
                "phone": phone,
                "base_fee": base_fee
            }

            try:
                with open(settings_file, 'w') as f:
                    json.dump(config, f, indent=4)

                flash("Settings saved successfully.", "success")
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f"Error saving settings: {e}", "danger")
                return redirect(url_for('settings'))

        # Carica le impostazioni esistenti
        current_settings = {}
        if os.path.exists(settings_file):
            with open(settings_file) as f:
                current_settings = json.load(f)

        return render_template('settings.html', settings=current_settings)


