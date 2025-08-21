import os
from typing import Any, Dict, List, TypedDict, Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from .a2a_client import RemoteA2AClient


class ClientState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    last_result: Any


def _extract_text_from_response(response: Any) -> str:
    """Best-effort extraction of assistant text from the A2A SDK response.

    Tries multiple known shapes, then falls back to scanning JSON for a 'text' field.
    """
    # 1) SDK attribute shape: response.root.result.message.parts[0].text
    try:
        parts = response.root.result.message.parts  # type: ignore[attr-defined]
        if parts and hasattr(parts[0], "text"):
            return parts[0].text  # type: ignore[no-any-return]
    except Exception:
        pass

    # 2) JSON dict shape
    try:
        as_json = response.model_dump(mode="json", exclude_none=True)  # type: ignore[attr-defined]
        # Try message.parts[0].text
        msg_parts = (
            as_json.get("root", {})
            .get("result", {})
            .get("message", {})
            .get("parts", [])
        )
        if isinstance(msg_parts, list) and msg_parts:
            text_val = msg_parts[0].get("text") or msg_parts[0].get("root", {}).get("text")
            if isinstance(text_val, str) and text_val:
                return text_val

        # Try artifacts → first text
        artifacts = (
            as_json.get("root", {})
            .get("result", {})
            .get("artifacts", [])
        )
        if isinstance(artifacts, list):
            for art in artifacts:
                # common shapes: { parts: [{ text: "..." }] } or { root: { text: "..." } }
                if isinstance(art, dict):
                    if "parts" in art and isinstance(art["parts"], list) and art["parts"]:
                        maybe_text = art["parts"][0].get("text")
                        if isinstance(maybe_text, str) and maybe_text:
                            return maybe_text
                    if "root" in art and isinstance(art["root"], dict):
                        maybe_text = art["root"].get("text")
                        if isinstance(maybe_text, str) and maybe_text:
                            return maybe_text

        # Fallback: deep search for first 'text' string
        def _dfs_find_text(node: Any) -> str | None:
            if isinstance(node, dict):
                if "text" in node and isinstance(node["text"], str):
                    return node["text"]
                for v in node.values():
                    found = _dfs_find_text(v)
                    if found:
                        return found
            if isinstance(node, list):
                for item in node:
                    found = _dfs_find_text(item)
                    if found:
                        return found
            return None

        fallback_text = _dfs_find_text(as_json)
        if isinstance(fallback_text, str) and fallback_text:
            return fallback_text
    except Exception:
        pass

    return ""


async def call_remote_agent(state: ClientState) -> Dict[str, Any]:
    user_message = state["messages"][-1]
    text = getattr(user_message, "content", None) or getattr(user_message, "text", "")
    base_url = os.getenv("A2A_REMOTE_URL", "http://localhost:10000")

    async with RemoteA2AClient(base_url=base_url) as remote:
        response = await remote.send_text(text)
        result_text = _extract_text_from_response(response) if response else ""

    return {
        "messages": [
            {
                "role": "assistant",
                "content": result_text or "(no content returned)",
            }
        ],
        "last_result": response.model_dump(mode="json", exclude_none=True) if response else None,
    }


def build_client_graph():
    graph = StateGraph(ClientState)
    graph.add_node("remote", call_remote_agent)
    graph.add_edge(START, "remote")
    graph.add_edge("remote", END)
    return graph.compile()


