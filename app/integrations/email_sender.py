import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings
from app.core.logger import request_logger


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    plain_body: Optional[str] = None,
) -> bool:
    """
    Send an email via SMTP. Returns True on success, False on failure.
    """
    if not settings.smtp_user or not settings.smtp_password or not settings.smtp_from_email:
        request_logger.error("SMTP credentials not configured; cannot send email")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        msg["To"] = to_email

        if plain_body:
            msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, to_email, msg.as_string())

        request_logger.info(f"Email sent to {to_email}: {subject}")
        return True

    except smtplib.SMTPAuthenticationError:
        request_logger.error("SMTP authentication failed — check smtp_user/smtp_password")
        return False
    except smtplib.SMTPException as e:
        request_logger.error(f"SMTP error sending to {to_email}: {str(e)}")
        return False
    except Exception as e:
        request_logger.error(f"Unexpected error sending email to {to_email}: {str(e)}")
        return False


def build_low_stock_email(
    product_name: str,
    current_qty: int,
    reorder_point: int,
    reorder_qty: int,
    tenant_name: str,
) -> tuple[str, str, str]:
    """Returns (subject, html_body, plain_body) for a low-stock supplier alert."""
    subject = f"Low Stock Alert: {product_name} — Reorder Required"

    plain_body = (
        f"Dear Supplier,\n\n"
        f"This is an automated alert from {tenant_name}.\n\n"
        f"Product: {product_name}\n"
        f"Current Stock: {current_qty} units\n"
        f"Reorder Threshold: {reorder_point} units\n"
        f"Suggested Reorder Quantity: {reorder_qty} units\n\n"
        f"Please arrange supply at your earliest convenience.\n\n"
        f"Regards,\n{tenant_name}"
    )

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto;">
        <div style="background:#f97316; padding:20px; border-radius:8px 8px 0 0;">
            <h2 style="color:#fff; margin:0;">&#9888; Low Stock Alert</h2>
        </div>
        <div style="border:1px solid #e5e7eb; border-top:none; padding:24px; border-radius:0 0 8px 8px;">
            <p>Dear Supplier,</p>
            <p>This is an automated alert from <strong>{tenant_name}</strong>. The following product has reached its reorder threshold and requires immediate restocking.</p>
            <table style="width:100%; border-collapse:collapse; margin:16px 0;">
                <tr style="background:#fef3c7;">
                    <td style="padding:10px; border:1px solid #fde68a; font-weight:bold;">Product</td>
                    <td style="padding:10px; border:1px solid #fde68a;">{product_name}</td>
                </tr>
                <tr>
                    <td style="padding:10px; border:1px solid #e5e7eb; font-weight:bold;">Current Stock</td>
                    <td style="padding:10px; border:1px solid #e5e7eb; color:#dc2626;"><strong>{current_qty} units</strong></td>
                </tr>
                <tr style="background:#f9fafb;">
                    <td style="padding:10px; border:1px solid #e5e7eb; font-weight:bold;">Reorder Threshold</td>
                    <td style="padding:10px; border:1px solid #e5e7eb;">{reorder_point} units</td>
                </tr>
                <tr>
                    <td style="padding:10px; border:1px solid #e5e7eb; font-weight:bold;">Suggested Reorder Qty</td>
                    <td style="padding:10px; border:1px solid #e5e7eb; color:#16a34a;"><strong>{reorder_qty} units</strong></td>
                </tr>
            </table>
            <p>Please arrange supply at your earliest convenience.</p>
            <p style="color:#6b7280; font-size:12px; margin-top:32px;">
                This is an automated message from {tenant_name}'s inventory management system. Please do not reply to this email.
            </p>
        </div>
    </body>
    </html>
    """

    return subject, html_body, plain_body
