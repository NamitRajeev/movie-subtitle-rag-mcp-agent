# scripts/test_mcp_email.py

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=["-u", "mcp/server.py"],
    )

    async with stdio_client(server_parameters) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            print("=" * 60)
            print("MCP EMAIL TEST")
            print("=" * 60)

            print("\nCalling send_email tool...")

            result = await session.call_tool(
                "send_email",
                {
                    "recipient": "rpptr0namit@gmail.com",
                    "subject": "Movie Subtitle RAG - MCP Test",
                    "body": (
                        "This is a test email from the "
                        "Movie Subtitle RAG MCP project."
                    ),
                },
            )

            print("\n" + "=" * 60)
            print("RAW TOOL RESULT")
            print("=" * 60)
            print(result)

            print("\n" + "=" * 60)
            print("RESULT CONTENT")
            print("=" * 60)

            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)
                else:
                    print(content)


if __name__ == "__main__":
    asyncio.run(main())