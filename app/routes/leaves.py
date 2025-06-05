from flask import Blueprint, request, redirect,render_template, url_for, flash, jsonify
from app.models import Employee, Leaves
from app.extensions import db
from datetime import date
from app.utils import login_required

leaves_bp = Blueprint('leaves', __name__)

@leaves_bp.route('/leaves', methods=['POST', 'GET'])
@login_required
def leaves_page():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        employee = Employee.query.filter_by(emp_id=emp_id).first()

        # Validate employee exists
        if not Employee.query.filter_by(emp_id=emp_id).first():
            flash('Invalid Employee ID!', 'danger')
            return redirect(url_for('leaves.leaves_page'))

        employee.job_status='on_leave'
        # db.session.flush()  # Get the leave ID
        new_leave=Leaves(
            emp_id=emp_id,
            leave_type = request.form['leave_type'],
            today_date = date.today(),
            start_date = request.form['start_date'],
            end_date = request.form['end_date'],
            reason = request.form['reason']

        )
        db.session.add(new_leave)
       
        
        db.session.commit()

        flash('Leave status updated', 'success')
        return redirect(url_for('attendance.view_attendance'))

    return render_template('leaves.html')

@leaves_bp.route('/validate_leave_id/<string:emp_id>', methods=['GET'])
@login_required
def validate_leave_id(emp_id):
    """Validate employee ID for leave requests"""
    employee = Employee.query.filter_by(emp_id=emp_id).first()
    return jsonify({'exists': bool(employee)})