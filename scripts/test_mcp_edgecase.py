# scripts/test_mcp_edge_cases.py

import importlib.util
from pathlib import Path

import pytest


# Load the project's mcp/server.py directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = PROJECT_ROOT / "mcp" / "server.py"

spec = importlib.util.spec_from_file_location(
    "movie_mcp_server",
    SERVER_PATH,
)

movie_mcp_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(movie_mcp_server)


def test_valid_recipient(monkeypatch):
    sent = {}

    def fake_send_email_smtp(
        recipient,
        subject,
        body,
    ):
        sent["recipient"] = recipient
        sent["subject"] = subject
        sent["body"] = body

    monkeypatch.setattr(
        movie_mcp_server,
        "send_email_smtp",
        fake_send_email_smtp,
    )

    result = movie_mcp_server.send_email(
        recipient="test@example.com",
        subject="MCP Test",
        body="Test email body.",
    )

    assert result == (
        "Email sent successfully to test@example.com."
    )

    assert sent["recipient"] == "test@example.com"
    assert sent["subject"] == "MCP Test"
    assert sent["body"] == "Test email body."


def test_invalid_recipient():
    with pytest.raises(
        ValueError,
        match="valid email address",
    ):
        movie_mcp_server.send_email(
            recipient="not-an-email",
            subject="MCP Test",
            body="Test email body.",
        )


def test_empty_body():
    with pytest.raises(
        ValueError,
        match="Body cannot be empty",
    ):
        movie_mcp_server.send_email(
            recipient="test@example.com",
            subject="MCP Test",
            body="",
        )


def test_smtp_failure(monkeypatch):
    def fake_send_email_smtp(
        recipient,
        subject,
        body,
    ):
        raise RuntimeError(
            "Simulated SMTP failure"
        )

    monkeypatch.setattr(
        movie_mcp_server,
        "send_email_smtp",
        fake_send_email_smtp,
    )

    result = movie_mcp_server.send_email(
        recipient="test@example.com",
        subject="MCP Test",
        body="Test email body.",
    )

    assert "email failed" in result.lower()
    assert "simulated smtp failure" in result.lower()


def test_mcp_unavailable():
    import asyncio

    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    missing_server = (
        PROJECT_ROOT
        / "mcp"
        / "server_file_that_does_not_exist.py"
    )

    assert not missing_server.exists()

    async def attempt_connection():
        server_parameters = StdioServerParameters(
            command="python",
            args=[
                str(missing_server),
            ],
        )

        async with stdio_client(
            server_parameters
        ) as (read, write):
            async with ClientSession(
                read,
                write,
            ) as session:
                await session.initialize()

    with pytest.raises(Exception):
        asyncio.run(
            attempt_connection()
        )