from flask_mail import Message
from .extensions import mail

def send_announcement(subject, recipients, message):
    msg = Message(
        subject=subject,
        recipients=recipients,
        body=message
    )
    mail.send(msg)