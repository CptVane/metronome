from datetime import datetime, timedelta

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