from mcp import ClientSession
from contextlib import AsyncExitStack
from mcp.client.streamable_http import streamablehttp_client
import os

class MCPHTTPCLIENT:
    def __init__(self,url):
        self.url = url
        self.exit_stack = AsyncExitStack()
        self.session = None

    async def connect(self):
        transport = await self.exit_stack.enter_async_context(
            streamablehttp_client(self.url)
        )

        # create MCP client session
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(*transport)
        )
        await self.session.initialize()

        return self.session

    async def list_tools(self):
        tool_list = await self.session.list_tools()
        return tool_list.tools

    async def cleanup(self):
        await self.exit_stack.aclose()
