from fastapi import APIRouter, HTTPException, status
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from core.config import config
from schemas.contact_schema import ContactForm

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

contact_router = APIRouter()


@contact_router.post("/contact")
async def send_contact_email(form_data: ContactForm):
    try:
        message = MessageSchema(
            subject="New Contact Form Submission",
            recipients=[config.MAIL_TO_ADDRESS],
            body=f"""
            <html>
                <body style="background-color:#f4f4f4; padding:30px;">
                    <div style="max-width:500px; margin:auto; background:#fff; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.08); padding:32px; font-family:Arial,sans-serif;">
                        <h2 style="color:#2d7ff9; margin-bottom:16px;">New Contact Message</h2>
                        <hr style="border:none; border-top:1px solid #eee; margin-bottom:24px;">
                        <p><strong>Name:</strong> {form_data.name}</p>
                        <p><strong>Email:</strong> <a href="mailto:{form_data.email}" style="color:#2d7ff9;">{form_data.email}</a></p>
                        <p><strong>Phone Number:</strong> <a href="tel:{form_data.phone_number}" style="color:#2d7ff9;">{form_data.phone_number}</a></p>
                        <p><strong>Preferred Contact Method:</strong> <span style="color:#444;">{form_data.preferred_contact_method.value.capitalize()}</span></p>
                        <p><strong>Subject:</strong> <span style="color:#444;">{form_data.subject}</span></p>
                        <div style="margin:24px 0;">
                            <strong>Message:</strong>
                            <div style="background:#f7faff; border-left:4px solid #2d7ff9; padding:16px; margin-top:8px; border-radius:4px; color:#222;">
                            {form_data.message}
                            </div>
                        </div>
                        <hr style="border:none; border-top:1px solid #eee; margin-top:32px;">
                        <p style="font-size:12px; color:#888; text-align:center;">This message was sent from your website contact form.</p>
                    </div>
                </body>
            </html>
            """,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        return {"message": "Email sent successfully!"}

    except Exception as e:
        print(f"Error sending email: {e}")  # Log the error for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email. Please try again later.",
        )
