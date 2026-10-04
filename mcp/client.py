# mcp/client.py

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

            tools_result = await session.list_tools()

            print("=" * 60)
            print("AVAILABLE MCP TOOLS")
            print("=" * 60)

            for tool in tools_result.tools:
                print(f"- {tool.name}")

            result = await session.call_tool(
                "send_email",
                {
                    "recipient": "example@gmail.com",
                    "subject": "MCP Test",
                    "body": "This is a test email from the Movie Subtitle RAG project.",
                },
            )

            print("\n" + "=" * 60)
            print("TOOL RESULT")
            print("=" * 60)

            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)
                else:
                    print(content)


if __name__ == "__main__":
    asyncio.run(main())