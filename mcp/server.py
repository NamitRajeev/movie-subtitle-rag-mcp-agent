# mcp/server.py

from mcp.server.mcpserver import MCPServer


mcp = MCPServer("Movie Subtitle Email Server")


@mcp.tool()
def send_email(
    recipient: str,
    subject: str,
    body: str,
) -> str:
    """
    Prepare an email to be sent to the specified recipient.

    SMTP integration will be added in the next step.
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
        raise ValueError("Recipient email address cannot be empty.")

    if not subject:
        raise ValueError("Subject cannot be empty.")

    if not body:
        raise ValueError("Body cannot be empty.")

    return (
        f"Email prepared for {recipient} "
        f"with subject '{subject}'."
    )


if __name__ == "__main__":
    mcp.run()