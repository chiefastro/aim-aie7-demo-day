import asyncio
import os

from langchain_core.messages import HumanMessage

from .agent import build_client_graph


async def run_once(prompt: str):
    graph = build_client_graph()
    result = await graph.ainvoke({"messages": [HumanMessage(content=prompt)]})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    prompt = os.getenv("CLIENT_PROMPT", "What are the latest developments in artificial intelligence?")
    asyncio.run(run_once(prompt))


