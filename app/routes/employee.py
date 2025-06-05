from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
import logging
from app.models import Employee,empTime,EmployeeSchema,Leaves
from app.extensions import db
import pandas as pd
from io import BytesIO
from sqlalchemy import or_
from app.utils import login_required

employee_bp = Blueprint('employee', __name__)
logger = logging.getLogger(__name__)

@employee_bp.route('/add_employee', methods=['POST','GET'])
@login_required
def add_employee():
    if request.method == 'POST':
        try:
            emp_id = request.form['emp_id']
            name = request.form['name']
            email = request.form['email']
            department = request.form['department']
            position = request.form['position']
            dob = request.form['dob']
            joining_date = request.form['joining_date']
            phone = request.form['phone']
            address = request.form['address']
            f_name = request.form['f_name']
            gender = request.form.get('gender')
            job_status = request.form.get('job_status')
            existing_emp = Employee.query.filter(
                or_(Employee.emp_id == emp_id, Employee.email == email)
            ).first()
            if existing_emp:
                if existing_emp.emp_id == emp_id:
                    flash('Employee ID already exists!', 'danger')
                elif existing_emp.email == email:
                    flash('Email already exists!', 'danger')
                return redirect(url_for('attendance.view_attendance'))
            new_emp = Employee(
                emp_id=emp_id,
                name=name,
                dob=dob,
                joining_date=joining_date,
                phone=phone,
                address=address,
                f_name=f_name,
                job_status=job_status,
                gender=gender,
                email=email,
                department=department,
                position=position
            )
            db.session.add(new_emp)
            db.session.commit()
            flash('New employee added successfully!', 'success')
            return redirect(url_for('attendance.view_attendance'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Add employee error: {e}")
            flash('A server error occurred. Please try again.', 'danger')
            return redirect(url_for('attendance.view_attendance'))
    return render_template('add_employee.html')

@employee_bp.route('/edit_employee/<string:emp_id>', methods=['GET', 'POST'])
@login_required
def edit_employee(emp_id):
    employee = Employee.query.filter_by(emp_id=emp_id).first_or_404()
    if request.method == 'POST':
        try:
            employee.name = request.form['name']
            employee.email = request.form['email']
            employee.department = request.form['department']
            employee.position = request.form['position']
            employee.dob = request.form['dob']
            employee.phone = request.form['phone']
            employee.address = request.form['address']
            employee.f_name = request.form['f_name']
            employee.job_status = request.form['job_status']
            db.session.commit()
            flash('Employee details updated successfully!', 'success')
            return redirect(url_for('attendance.view_attendance'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Edit employee error: {e}")
            flash('A server error occurred. Please try again.', 'danger')
            return redirect(url_for('attendance.view_attendance'))
    return render_template('edit_employee.html', employee=employee)

@employee_bp.route('/delete_attendance/<string:emp_id>', methods=['POST'])
@login_required
def delete_attendance(emp_id):
    try:
        print(f"Attempting to delete employee: {emp_id}")  # Debug line
        employee = Employee.query.filter_by(emp_id=emp_id).first_or_404()
        empTime.query.filter_by(emp_id=emp_id).delete()
        EmployeeSchema.query.filter_by(emp_id=emp_id).delete()
        Leaves.query.filter_by(emp_id=emp_id).delete()
        db.session.delete(employee)
        db.session.commit()
        flash('Employee and related records deleted successfully!', 'success')
        return redirect(url_for('employee.employees'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete employee error: {e}")
        flash('A server error occurred. Please try again.', 'danger')
        return redirect(url_for('employee.employees'))

@employee_bp.route('/employees')
@login_required
def employees():
    try:
        employees = Employee.query.all()
        return render_template('employees.html', records=employees)
    except Exception as e:
        logger.error(f"View employees error: {e}")
        flash('A server error occurred. Please try again.', 'danger')
        return render_template('employees.html', records=[])

@employee_bp.route('/download_employee/')
@login_required
def download_employee():
    try:
        record = Employee.query.all()
        data = [{
            'Employee ID': a.emp_id,
            'Employee Name': a.name,
            'Father Name': a.f_name,
            'Date of Birth': a.dob,
            'Gender': a.gender,
            'Contact': a.phone,
            'Email': a.email,
            'Address': a.address,
            'Status': a.job_status,
            'Department': a.department,
            'Position': a.position,
            'Date of Joining': a.joining_date
        } for a in record]
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
        logger.error(f"Download employee error: {e}")
        flash('A server error occurred. Please try again.', 'danger')
        return redirect(url_for('employee.employees'))