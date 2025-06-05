from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
import logging
from app.models import Employee, EmployeeSchema, empTime, EmployeeSchemaArchive, empTimeArchive
from app.extensions import db
from datetime import date, datetime, timedelta
from sqlalchemy import func
import pandas as pd
from io import BytesIO
from app.models import current_ist_time
from app.utils import login_required
from app.auth_utils import verify_code, set_verification_code  # Make sure to create this file as described

attendance_bp = Blueprint('attendance', __name__)
logger = logging.getLogger(__name__)

@attendance_bp.route('/mark', methods=['GET', 'POST'])
def mark_attendance():
    def process_attendance(emp_id, status, latitude, longitude, verification_code):
        try:
            if not emp_id or not status:
                return {'success': False, 'error': 'Employee ID is missing'}
            emp = Employee.query.filter_by(emp_id=emp_id).first()
            if not emp:
                return {'success': False, 'error': 'Invalid Employee ID!'}
            if emp.job_status != 'active':
                return {'success': False, 'error': 'Employee is not active'}
            if not verification_code or not verify_code(emp_id, verification_code):
                return {'success': False, 'error': 'Invalid or expired verification code. Please check your email or resend.'}
            last_record = EmployeeSchema.query.filter_by(emp_id=emp.emp_id).order_by(EmployeeSchema.ES_id.desc()).first()
            if not last_record:
                if status == 'Check-out':
                    return {'success': False, 'error': 'You must check in first before checking out.'}
            else:
                if last_record.status == status:
                    return {'success': False, 'error': f'Already {status.lower()}ed. Please do the opposite action first.'}
                if last_record.status == 'Check-out' and status == 'Check-out':
                    return {'success': False, 'error': 'You have already checked out. Please check in first.'}
                if last_record.status != 'Check-in' and status == 'Check-out':
                    return {'success': False, 'error': 'You must check in first before checking out.'}
            new_record = EmployeeSchema(
                name=emp.name,
                emp_id=emp.emp_id,
                email=emp.email,
                department=emp.department,
                position=emp.position,
                status=status,
                latitude=latitude,
                longitude=longitude,
                today_date=date.today(),
                time=current_ist_time().time()
            )
            db.session.add(new_record)
            new_time = empTime(
                emp_id=emp.emp_id,
                name=emp.name,
                status=status,
                today_date=date.today(),
                time=current_ist_time().time()
            )
            db.session.add(new_time)
            db.session.commit()
            return {'success': True}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Attendance processing error: {e}")
            return {'success': False, 'error': 'A server error occurred. Please try again.'}
    # Handle API requests (JSON)
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        try:
            api_key = request.headers.get('X-API-KEY')
            if api_key != current_app.config.get('VALID_KEY'):
                return jsonify({'success': False, 'error': 'Forbidden'}), 403
            data = request.get_json()
            emp_id = data.get('emp_id')
            status = data.get('status')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            verification_code = data.get('verification_code')
            result = process_attendance(emp_id, status, latitude, longitude, verification_code)
            return jsonify(result)
        except Exception as e:
            logger.error(f"API attendance error: {e}")
            return jsonify({'success': False, 'error': 'A server error occurred.'}), 500
    # Handle web form submissions
    if request.method == 'POST':
        try:
            emp_id = request.form.get('emp_id')
            status = request.form.get('status')
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            verification_code = request.form.get('verification_code')
            result = process_attendance(emp_id, status, latitude, longitude, verification_code)
            if result['success']:
                flash('Attendance marked successfully', 'success')
                return redirect(url_for('attendance.mobile_attendance'))  # <-- redirect after success
            else:
                flash(result['error'], 'danger')
            return render_template('mobile/mobile-attendance.html')
        except Exception as e:
            logger.error(f"Web attendance error: {e}")
            flash('A server error occurred. Please try again.', 'danger')
            return render_template('mobile/mobile-attendance.html')
    # GET request
    return render_template('mobile/mobile-attendance.html')

@attendance_bp.route('/attendance')
@login_required
def view_attendance():
    try:
        # Summary Stats
        total_employees = Employee.query.count()
        # For each employee, get their latest empTime record for today, and count if it's 'Check-in'
        subquery = db.session.query(
            empTime.emp_id,
            func.max(empTime.emptime_id).label('max_id')
        ).filter(empTime.today_date == date.today()).group_by(empTime.emp_id).subquery()

        present_today_q = db.session.query(
            empTime.emp_id,
            empTime.name,
            Employee.department,
            Employee.position
        ).join(
            subquery, empTime.emptime_id == subquery.c.max_id
        ).join(
            Employee, empTime.emp_id == Employee.emp_id
        ).filter(empTime.status == 'Check-in')
        present_today= present_today_q.count()
        present_today_records = present_today_q.all()


        # Attendance trends (last 7 days)
        today = datetime.today()
        dates = [(today - timedelta(days=i)).date() for i in range(7)][::-1]  # Last 7 days

        attendance_data = {
            'dates': [d.strftime('%Y-%m-%d') for d in dates],
            'checkins': [],
            'checkouts': [],
        }
        employees_on_leave = Employee.query.filter_by(job_status='on_leave').count()

        for d in dates:
            checkins = empTime.query.filter_by(today_date=d, status='Check-in').count()
            checkouts = empTime.query.filter_by(today_date=d, status='Check-out').count()
            attendance_data['checkins'].append(checkins)
            attendance_data['checkouts'].append(checkouts)

        # Department distribution
        dept_data = db.session.query(
            Employee.department,
            func.count(Employee.emp_id)
        ).group_by(Employee.department).all()

        # For pie chart
        dept_labels = [d[0] for d in dept_data]
        dept_counts = [d[1] for d in dept_data]

        # Recent Activity (limit to last 10, if applicable)
        recent_activity = db.session.query(EmployeeSchema).order_by(EmployeeSchema.ES_id.desc()).limit(10).all()

        # Full employee records for table
        records = Employee.query.all()

        return render_template(
            'attendance.html',
            total_employees=total_employees,
            present_today=present_today,
            present_today_records=present_today_records,
            employees_on_leave=employees_on_leave,
            total_departments=len(dept_labels),
            attendance_dates=attendance_data.get('dates',[]),
            checkin_counts=attendance_data.get('checkins',[]),
            checkout_counts=attendance_data.get('checkouts',[]),
            departments=dept_labels,
            department_counts=dept_counts,
            recent_activity=recent_activity,
            records=records
        )
    except Exception as e:
        logger.error(f"Attendance dashboard error: {e}")
        flash('A server error occurred. Please try again.', 'danger')
        return render_template('attendance.html')

@attendance_bp.route('/attendance_time/<string:name>')
@login_required
def view_attendance_time(name):
    try:
        records = empTime.query.filter_by(name=name).all()
        return render_template('attendance_time.html', records=records, employee_name=name)
    except Exception as e:
        logger.error(f"Attendance time view error: {e}")
        flash('A server error occurred. Please try again.', 'danger')
        return render_template('attendance_time.html', records=[], employee_name=name)

@attendance_bp.route('/validate_id/<string:emp_id>', methods=['GET'])
@login_required
def validate_employee(emp_id):
    try:
        employee = Employee.query.filter_by(emp_id=emp_id).first()
        if employee:
            return jsonify({
                'exists': True,
                'name': employee.name,
                'email': employee.email,
                'department': employee.department,
                'position': employee.position
            })
        return jsonify({'exists': False})
    except Exception as e:
        logger.error(f"Validate employee error: {e}")
        return jsonify({'exists': False, 'error': 'Server error'})

@attendance_bp.route('/download_attendance')
@login_required
def download_attendance():
    try:
        main_records = EmployeeSchema.query.all()
        archive_records = EmployeeSchemaArchive.query.all()
        records = list(main_records) + list(archive_records)
        data = [{
            'Type': 'Attendance',
            'Employee ID': a.emp_id,
            'Name': a.name,
            'Email': a.email,
            'Department': a.department,
            'Position': a.position,
            'Status/Leave Type': a.status,
            'Date': a.today_date.strftime('%Y-%m-%d'),
            'Time': a.time.strftime('%H:%M:%S'),
            'Latitude': a.latitude,
            'Longitude': a.longitude,
            'Reason': '',
            'Start Date': '',
            'End Date': ''
        } for a in records]
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Attendance')
        output.seek(0)
        return send_file(output,
                         as_attachment=True,
                         download_name='attendance.xlsx',
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        logger.error(f"Download attendance error: {e}")
        flash('A server error occurred. Please try again.', 'danger')
        return redirect(url_for('attendance.view_attendance'))

@attendance_bp.route('/mobile_attendance', methods=['GET'])
def mobile_attendance():
    return render_template('mobile/mobile-attendance.html')

@attendance_bp.route('/resend_code', methods=['POST'])
def resend_code():
    try:
        emp_id = request.form.get('emp_id')
        emp = Employee.query.filter_by(emp_id=emp_id).first()
        if not emp:
            flash('Invalid Employee ID!', 'danger')
            return '', 400
        set_verification_code(emp_id)
        return '', 204
    except Exception as e:
        logger.error(f"Resend code error: {e}")
        flash('A server error occurred. Please try again.', 'danger')
        return '', 500

@attendance_bp.route('/download_attendance_time')
@login_required
def download_attendance_time():
    try:
        records = empTime.query.all()
        data = [{
            'Employee Name': r.name,
            'Attendance Time': r.time.strftime('%H:%M:%S') if r.time else '',
            'Attendance Date': r.today_date.strftime('%Y-%m-%d') if r.today_date else '',
            'Status': r.status
        } for r in records]
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='AttendanceTime')
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name='attendance_time.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logger.error(f"Download attendance time error: {e}")
        flash('A server error occurred. Please try again.', 'danger')
        return redirect(url_for('attendance.view_attendance'))