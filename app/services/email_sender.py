import resend
from app.config import settings

resend.api_key = settings.RESEND_API_KEY


def send_digest_email(to_email: str, subject: str, html_body: str) -> str | None:
    """
    Sends the digest email using Resend.
    Returns the message ID if successful, otherwise None.
    """
    if not settings.RESEND_API_KEY:
        print("RESEND_API_KEY not set")
        return None

    try:
        response = resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        })
        return response.get("id")
    except Exception as e:
        print(f"Failed to send email: {e}")
        return None

def send_otp_email(to_email: str, code: str) -> str | None:
    """
    Sends a 6-digit OTP code to the user.
    """
    if not settings.RESEND_API_KEY:
        print(f"RESEND_API_KEY not set. OTP for {to_email} is {code}")
        return None

    html_body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Verify your email</h2>
        <p>Your verification code for Daily Digest is:</p>
        <h1 style="letter-spacing: 4px; color: #1b4d32; background: #e8f3ed; padding: 12px; text-align: center; border-radius: 8px;">{code}</h1>
        <p>This code will expire in 15 minutes.</p>
    </div>
    """
    
    try:
        response = resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [to_email],
            "subject": "Your Daily Digest verification code",
            "html": html_body,
        })
        return response.get("id")
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return None


def send_password_reset_email(to_email: str, reset_url: str) -> str | None:
    if not settings.RESEND_API_KEY:
        print(f"RESEND_API_KEY not set. Password reset link for {to_email}: {reset_url}")
        return None

    html_body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Reset your password</h2>
        <p>We received a request to reset your Daily Digest password.</p>
        <p style="margin: 24px 0;">
            <a href="{reset_url}" style="background:#1a1a2e; color:#ffffff; padding:12px 20px; border-radius:999px; text-decoration:none;">
                Choose a new password
            </a>
        </p>
        <p>This link expires in 1 hour. If you did not request it, you can ignore this email.</p>
    </div>
    """

    try:
        response = resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [to_email],
            "subject": "Reset your Daily Digest password",
            "html": html_body,
        })
        return response.get("id")
    except Exception as e:
        print(f"Failed to send password reset email: {e}")
        return None