from pydantic_ai import Agent
from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPServerStdio
import os

from pydantic import BaseModel

class AgentOutput(BaseModel):
    output: str

system_prompt = """
You are an online music store agent tasked to retrieve a list of song tracks.
Only base your reply on the context provided.
"""

class QNAAgent:
    def __init__(self,nvidia_api_key,mcp_server_qna_path,inf_url):
        self.mcp_server = MCPServerStdio(
            command="uv",
            args=[
                "--directory",
                mcp_server_qna_path,
                "run",
                "mcp-server-qna",
                "--db-path",
                "data/chinook.db"
            ]
        )

        self.agent = Agent(
            model = OpenAIModel(
                model_name="nvidia/llama-3.3-nemotron-super-49b-v1.5",
                provider=OpenAIProvider(
                    api_key=nvidia_api_key,
                    base_url=inf_url
                )
            ),
            system_prompt=system_prompt,
            mcp_servers=[self.mcp_server],
            output=AgentOutput
        )
        ## TODO
        ## define MCP server, model and agent``
        pass

    async def run(self, query):
        async with self.agent.run_mcp_servers():
            result = await self.agent.run(query)
        return result.output
        ## TODO
        ## run agent with mcp servers and return output
        pass