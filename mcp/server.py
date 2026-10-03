import os
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage
from email.utils import parseaddr

from mcp.server.mcpserver import MCPServer


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


mcp = MCPServer("Movie Subtitle Email Server")


def send_email_smtp(
    recipient: str,
    subject: str,
    body: str,
) -> None:
    """
    Send an email using the configured SMTP server.
    """

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_host:
        raise ValueError("SMTP_HOST is not configured.")

    if not smtp_port:
        raise ValueError("SMTP_PORT is not configured.")

    if not smtp_username:
        raise ValueError("SMTP_USERNAME is not configured.")

    if not smtp_password:
        raise ValueError("SMTP_PASSWORD is not configured.")

    try:
        smtp_port = int(smtp_port)
    except ValueError:
        raise ValueError("SMTP_PORT must be a valid integer.")

    message = EmailMessage()
    message["From"] = smtp_username
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(
            smtp_host,
            smtp_port,
            timeout=30,
        ) as server:
            server.starttls()
            server.login(
                smtp_username,
                smtp_password,
            )
            server.send_message(message)

    except smtplib.SMTPException as exc:
        raise RuntimeError(f"SMTP error: {exc}") from exc


@mcp.tool()
def send_email(
    recipient: str,
    subject: str,
    body: str,
) -> str:
    """
    Send an email to the specified recipient.
    """

    if not isinstance(recipient, str):
        raise ValueError("Recipient must be a string.")

    if not isinstance(subject, str):
        raise ValueError("Subject must be a string.")

    if not isinstance(body, str):
        raise ValueError("Body must be a string.")

    recipient = recipient.strip()
    subject = subject.strip()
    body = body.strip()

    if not recipient:
        raise ValueError(
            "Recipient email address cannot be empty."
        )

    _, parsed_recipient = parseaddr(recipient)

    if not parsed_recipient or "@" not in parsed_recipient:
        raise ValueError(
            "Recipient must be a valid email address."
        )

    if not subject:
        raise ValueError("Subject cannot be empty.")

    if not body:
        raise ValueError("Body cannot be empty.")

    try:
        send_email_smtp(
            recipient=recipient,
            subject=subject,
            body=body,
        )
    except Exception as exc:
        return f"Email failed: {type(exc).__name__}: {exc}"

    return f"Email sent successfully to {recipient}."


if __name__ == "__main__":
    mcp.run()