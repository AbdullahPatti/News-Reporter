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
        <p>Your verification code for News Reporter is:</p>
        <h1 style="letter-spacing: 4px; color: #4f46e5; background: #f5f3ff; padding: 12px; text-align: center; border-radius: 8px;">{code}</h1>
        <p>This code will expire in 15 minutes.</p>
    </div>
    """
    
    try:
        response = resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [to_email],
            "subject": "Your News Reporter Verification Code",
            "html": html_body,
        })
        return response.get("id")
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return None