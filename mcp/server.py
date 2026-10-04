import os
import smtplib
import time

from dotenv import load_dotenv
from email.message import EmailMessage
from email.utils import parseaddr

from mcp.server.mcpserver import MCPServer


# -------------------------------------------------------------
# Environment
# -------------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

load_dotenv(
    os.path.join(
        BASE_DIR,
        ".env",
    )
)


# -------------------------------------------------------------
# MCP server
# -------------------------------------------------------------

mcp = MCPServer(
    "Movie Subtitle Email Server"
)


# -------------------------------------------------------------
# SMTP
# -------------------------------------------------------------

def send_email_smtp(
    recipient: str,
    subject: str,
    body: str,
) -> None:
    """
    Send an email using the configured SMTP server.

    Retries transient network failures because SMTP
    connections can occasionally time out.
    """

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    # ---------------------------------------------------------
    # Validate SMTP configuration
    # ---------------------------------------------------------

    if not smtp_host:
        raise ValueError(
            "SMTP_HOST is not configured."
        )

    if not smtp_port:
        raise ValueError(
            "SMTP_PORT is not configured."
        )

    if not smtp_username:
        raise ValueError(
            "SMTP_USERNAME is not configured."
        )

    if not smtp_password:
        raise ValueError(
            "SMTP_PASSWORD is not configured."
        )

    try:
        smtp_port = int(smtp_port)
    except ValueError:
        raise ValueError(
            "SMTP_PORT must be a valid integer."
        )

    # ---------------------------------------------------------
    # Build email
    # ---------------------------------------------------------

    message = EmailMessage()

    message["From"] = smtp_username
    message["To"] = recipient
    message["Subject"] = subject

    message.set_content(body)

    # ---------------------------------------------------------
    # SMTP sending with retry
    # ---------------------------------------------------------

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

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

                server.send_message(
                    message
                )

            # Email sent successfully.
            return

        except (TimeoutError, OSError) as exc:

            if attempt == max_attempts:
                raise RuntimeError(
                    f"SMTP connection failed after "
                    f"{max_attempts} attempts: {exc}"
                ) from exc

            # Exponential-style backoff:
            # attempt 1 -> 2 seconds
            # attempt 2 -> 4 seconds
            time.sleep(attempt * 2)

        except smtplib.SMTPException as exc:
            # SMTP protocol/authentication errors should
            # not be blindly retried.
            raise RuntimeError(
                f"SMTP error: {exc}"
            ) from exc


# -------------------------------------------------------------
# MCP tool
# -------------------------------------------------------------

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
        raise ValueError(
            "Recipient must be a string."
        )

    if not isinstance(subject, str):
        raise ValueError(
            "Subject must be a string."
        )

    if not isinstance(body, str):
        raise ValueError(
            "Body must be a string."
        )

    recipient = recipient.strip()
    subject = subject.strip()
    body = body.strip()

    # ---------------------------------------------------------
    # Validate recipient
    # ---------------------------------------------------------

    if not recipient:
        raise ValueError(
            "Recipient email address cannot be empty."
        )

    _, parsed_recipient = parseaddr(
        recipient
    )

    if (
        not parsed_recipient
        or "@" not in parsed_recipient
    ):
        raise ValueError(
            "Recipient must be a valid email address."
        )

    # ---------------------------------------------------------
    # Validate subject
    # ---------------------------------------------------------

    if not subject:
        raise ValueError(
            "Subject cannot be empty."
        )

    # ---------------------------------------------------------
    # Validate body
    # ---------------------------------------------------------

    if not body:
        raise ValueError(
            "Body cannot be empty."
        )

    # ---------------------------------------------------------
    # Send email
    # ---------------------------------------------------------

    try:
        send_email_smtp(
            recipient=recipient,
            subject=subject,
            body=body,
        )

    except Exception as exc:
        return (
            f"Email failed: "
            f"{type(exc).__name__}: {exc}"
        )

    return (
        f"Email sent successfully to "
        f"{recipient}."
    )


# -------------------------------------------------------------
# MCP server entry point
# -------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()