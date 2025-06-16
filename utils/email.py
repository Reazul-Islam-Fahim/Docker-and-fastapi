import smtplib
from email.message import EmailMessage
from config import settings
import logging

def send_email(to_email: str, subject: str, html_content: str):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
        msg["To"] = to_email
        msg.set_content("This is an HTML email. Please view it in an HTML-compatible client.")
        msg.add_alternative(html_content, subtype="html")

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD.strip())
            server.send_message(msg)

        logging.info(f"Email sent to {to_email}")
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {e}")
       
