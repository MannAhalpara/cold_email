import imaplib
import smtplib
import time
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def send_email(
    sender_email: str,
    app_password: str,
    receiver_email: str,
    subject: str,
    body: str,
    attachment_path: str = None,
):
    """Send an email directly via Gmail SMTP."""
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(
        MIMEText(body, "plain", "utf-8")
    )

    if attachment_path:
        att_file = Path(attachment_path)
        if att_file.exists():
            with open(att_file, "rb") as f:
                part = MIMEApplication(f.read(), Name=att_file.name)
            part['Content-Disposition'] = f'attachment; filename="{att_file.name}"'
            message.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(message)

    print(f"[SUCCESS] Email directly sent to {receiver_email}")


def save_draft_gmail(
    sender_email: str,
    app_password: str,
    receiver_email: str,
    subject: str,
    body: str,
    attachment_path: str = None,
):
    """Save an email as a draft directly inside Gmail via IMAP with optional attachment."""
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(
        MIMEText(body, "plain", "utf-8")
    )

    if attachment_path:
        att_file = Path(attachment_path)
        if att_file.exists():
            with open(att_file, "rb") as f:
                part = MIMEApplication(f.read(), Name=att_file.name)
            part['Content-Disposition'] = f'attachment; filename="{att_file.name}"'
            message.attach(part)

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

    print(f"[SUCCESS] Email draft successfully saved inside Gmail for {receiver_email}")


def send_otp_email(receiver_email: str, otp_code: str):
    """Send OTP email using Gmail credentials from environment variables (supports Port 465 SSL and Port 587 TLS)."""
    import os
    sender_email = (
        os.getenv("authentication_email") or os.getenv("AUTHENTICATION_EMAIL") or ""
    ).strip()
    raw_password = (
        os.getenv("authentication_password") or os.getenv("AUTHENTICATION_PASSWORD") or ""
    ).strip()
    app_password = raw_password.replace(" ", "")

    if not sender_email or not app_password:
        print("[ERROR] Gmail credentials missing from environment variables!")
        raise RuntimeError("Gmail credentials (authentication_email / authentication_password) missing from environment variables")

    subject = "Your Verification Code - Cold Email Platform"
    body = (
        f"Your verification code is: {otp_code}\n\n"
        "This code will expire in 10 minutes.\n"
        "If you did not request this login code, please ignore this message."
    )

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain", "utf-8"))

    # Attempt 1: Port 465 SSL (Direct SSL, best for cloud environments like Render)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(sender_email, app_password)
            server.send_message(message)
        print(f"[SUCCESS] OTP email sent to {receiver_email} via Port 465 (SSL)")
        return
    except Exception as e1:
        print(f"[WARNING] Port 465 SSL failed ({e1}), falling back to Port 587 TLS...")

    # Attempt 2: Port 587 TLS (Fallback)
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(message)
        print(f"[SUCCESS] OTP email sent to {receiver_email} via Port 587 (TLS)")
        return
    except Exception as e2:
        print(f"[ERROR] Both SMTP connections (465 SSL & 587 TLS) failed: {e2}")
        raise RuntimeError(f"SMTP delivery failed: {e2}")