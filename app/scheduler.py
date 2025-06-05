from apscheduler.schedulers.background import BackgroundScheduler
from .models import Employee, Leaves
from .extensions import db
from datetime import date

def employee_status_updater():
    with db.app.app_context():
        today = date.today()
        employees_on_leave = Employee.query.filter(Employee.job_status != 'active').all()

        update_ids = set()

        for emp in employees_on_leave:
            future_or_current_leave = Leaves.query.filter(
                Leaves.emp_id == emp.emp_id,
                Leaves.start_date <= today,
                Leaves.end_date >= today
            ).first()

            if not future_or_current_leave:
                emp.job_status = 'active'
                update_ids.add(emp.emp_id)
        
        db.session.commit()
        print(f"[Scheduler] Reactivated {len(update_ids)} employee(s).")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(employee_status_updater, 'cron', hour=0, minute=0)
    scheduler.start()