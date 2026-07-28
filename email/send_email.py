import imaplib
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(
    sender_email: str,
    app_password: str,
    receiver_email: str,
    subject: str,
    body: str,
):
    """Send an email directly via Gmail SMTP."""
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(
        MIMEText(body, "plain", "utf-8")
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(message)

    print(f"✅ Email directly sent to {receiver_email}")


def save_draft_gmail(
    sender_email: str,
    app_password: str,
    receiver_email: str,
    subject: str,
    body: str,
):
    """Save an email as a draft directly inside Gmail via IMAP."""
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(
        MIMEText(body, "plain", "utf-8")
    )

    now = imaplib.Time2Internaldate(time.time())

    with imaplib.IMAP4_SSL("imap.gmail.com", 993) as imap:
        imap.login(sender_email, app_password)

        # Standard Gmail Drafts folder in IMAP is '[Gmail]/Drafts'
        # Fallback to 'Drafts' if standard folder name fails
        res, data = imap.append('"[Gmail]/Drafts"', r'(\Draft)', now, message.as_bytes())
        if res != "OK":
            res, data = imap.append("Drafts", r'(\Draft)', now, message.as_bytes())
            if res != "OK":
                raise RuntimeError(f"Failed to save draft in Gmail IMAP: {data}")

    print(f"✅ Email draft successfully saved inside Gmail for {receiver_email}")