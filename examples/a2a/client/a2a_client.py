import logging
from typing import Any
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
)
from a2a.utils.constants import (
    AGENT_CARD_WELL_KNOWN_PATH,
    EXTENDED_AGENT_CARD_PATH,
)


logger = logging.getLogger(__name__)


class RemoteA2AClient:
    """Thin reusable wrapper around the A2A client for our remote agent server."""

    def __init__(self, base_url: str = "http://localhost:10000", timeout_seconds: float = 60.0):
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.httpx_client: httpx.AsyncClient | None = None
        self.agent_card: AgentCard | None = None
        self.client: A2AClient | None = None

    async def __aenter__(self) -> "RemoteA2AClient":
        await self._init()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.httpx_client:
            await self.httpx_client.aclose()

    async def _init(self) -> None:
        """Initialize HTTP client, resolve agent card, and create A2A client."""
        if self.httpx_client is None:
            self.httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(self.timeout_seconds))

        resolver = A2ACardResolver(
            httpx_client=self.httpx_client, base_url=self.base_url
        )

        # Fetch public card
        logger.info(
            f"Fetching public agent card from: {self.base_url}{AGENT_CARD_WELL_KNOWN_PATH}"
        )
        public_card = await resolver.get_agent_card()
        card_to_use: AgentCard = public_card

        # Try extended card if supported (best-effort)
        if public_card.supports_authenticated_extended_card:
            try:
                logger.info(
                    f"Attempting to fetch extended agent card from: {self.base_url}{EXTENDED_AGENT_CARD_PATH}"
                )
                auth_headers_dict = {"Authorization": "Bearer dummy-token-for-extended-card"}
                extended_card = await resolver.get_agent_card(
                    relative_card_path=EXTENDED_AGENT_CARD_PATH,
                    http_kwargs={"headers": auth_headers_dict},
                )
                card_to_use = extended_card
                logger.info("Using authenticated extended agent card.")
            except Exception as e:
                logger.warning(
                    f"Failed to fetch extended agent card: {e}. Falling back to public card.",
                    exc_info=True,
                )

        self.agent_card = card_to_use
        self.client = A2AClient(httpx_client=self.httpx_client, agent_card=self.agent_card)
        logger.info("A2AClient initialized.")

    async def send_text(self, text: str, *, task_id: str | None = None, context_id: str | None = None) -> Any:
        """Send a single-turn text message. Returns the raw SDK response object."""
        if self.client is None:
            await self._init()
        assert self.client is not None

        payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
                "message_id": uuid4().hex,
            },
        }
        if task_id:
            payload["message"]["task_id"] = task_id
        if context_id:
            payload["message"]["context_id"] = context_id

        request = SendMessageRequest(id=str(uuid4()), params=MessageSendParams(**payload))
        return await self.client.send_message(request)


