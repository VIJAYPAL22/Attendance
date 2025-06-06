from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import SystemLog, EmployeeSchema, empTime, EmployeeSchemaArchive, empTimeArchive
from app.extensions import db
from datetime import date, datetime
import pytz
from config import Config
from app.utils import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        key = request.form['secret_key']
        if key == Config.VALID_KEY:
            ist = pytz.timezone('Asia/Kolkata')
            today_ist = datetime.now(ist).date()

            system_log = SystemLog.query.order_by(SystemLog.id.desc()).first()
            if not system_log:
                new_log = SystemLog(last_reset_date=today_ist)
                db.session.add(new_log)
                db.session.commit()
            else:
                last_reset = system_log.last_reset_date
                if last_reset < today_ist:
                    try:
                        # Archive and clear EmployeeSchema
                        emp_schemas = EmployeeSchema.query.all()
                        for emp in emp_schemas:
                            archived = EmployeeSchemaArchive(
                                name=emp.name,
                                emp_id=emp.emp_id,
                                email=emp.email,
                                department=emp.department,
                                position=emp.position,
                                status=emp.status,
                                today_date=emp.today_date,
                                time=emp.time,
                                latitude=emp.latitude,
                                longitude=emp.longitude
                            )
                            db.session.add(archived)
                        db.session.commit()
                        EmployeeSchema.query.delete()

                        # Archive and clear empTime
                        emp_times = empTime.query.all()
                        for et in emp_times:
                            archived_et = empTimeArchive(
                                emp_id=et.emp_id,
                                name=et.name,
                                status=et.status,
                                today_date=et.today_date,
                                time=et.time
                            )
                            db.session.add(archived_et)
                        db.session.commit()
                        empTime.query.delete()
                        
                    except Exception as e:
                        db.session.rollback()
                        flash(f'Error during archiving: {str(e)}', 'danger')
                        return redirect(url_for('login'))
            # Set session and redirect after successful login
            session['logged_in'] = True
            valid_login = True
            if valid_login:
                # For mobile, redirect to attendance page
                if request.user_agent.platform in ['android', 'iphone']:
                    return render_template('login.html', next_url=url_for('attendance.mobile_attendance'))
                else:
                    return redirect(url_for('attendance.view_attendance'))
        else:
            flash('Invalid Key', 'danger')
            return render_template('login.html')
    # For GET requests or any other case, render the login page
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login'))