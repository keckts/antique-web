# accounts/utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import random

# def send_verification_email(user, code):
#     subject = 'Verify your email'
#     from_email = settings.DEFAULT_FROM_EMAIL
#     to_email = [user.email]

#     # Render HTML template
#     html_content = render_to_string('accounts/email_verification.html', {'code': code, 'user': user})
    
#     msg = EmailMultiAlternatives(subject, '', from_email, to_email)
#     msg.attach_alternative(html_content, "text/html")
#     msg.send()

from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_verification_email(user, code):
    subject = "Verify your email"
    html_message = render_to_string("emails/verify_email.html", {"user": user, "code": code})
    send_mail(
        subject,
        "",  # plain text fallback
        "no-reply@example.com",
        [user.email],
        html_message=html_message,
    )


def generate_verification_code():
    return f"{random.randint(100000, 999999)}"

import requests
from django.conf import settings

def send_mailerlite_email(to_email, subject, html_content):
    url = "https://api.mailerlite.com/api/v2/email/send"
    headers = {
        "Content-Type": "application/json",
        "X-MailerLite-ApiKey": settings.MAILERLITE_API_KEY,
    }
    payload = {
        "subject": subject,
        "from": {"email": "edwardsemporiumau@gmail.com", "name": "Edward's Emporium"},
        "to": [{"email": to_email}],
        "html": html_content,
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return True
    else:
        print(response.text)
        return False
