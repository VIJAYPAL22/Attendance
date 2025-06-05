from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import Employee
from app.extensions import db, mail
from flask_mail import Message
from config import Config
from app.utils import login_required

announcement_bp = Blueprint('announcement', __name__)

@announcement_bp.route('/Announcements', methods=['POST', 'GET'])
@login_required
def Announcements():
    if request.method == 'POST':
        message = request.form['message']
        department = request.form['department']

        if department == 'all':
            recipients = Employee.query.all()
        else:
            recipients = Employee.query.filter_by(department=department).all()

        if not recipients:
            flash('No employees found!', 'danger')
            return redirect(url_for('Announcements'))

        email_list = [emp.email for emp in recipients]

        try:
            msg = Message(
                subject='AH&V Announcement',
                sender=Config.MAIL_USERNAME,
                recipients=email_list,
                body=message
            )
            mail.send(msg)
            flash(f'Announcement sent to {len(email_list)} employees!', 'success')
        except Exception as e:
            flash(f'Failed to send emails: {str(e)}', 'danger')

        return redirect(url_for('announcement.Announcements'))

    departments = db.session.query(Employee.department).distinct().all()
    departments = [d[0] for d in departments]
    return render_template('announcements.html', departments=departments)