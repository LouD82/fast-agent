"""
FastAgent - A simple agent implementation for fast-agent.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union

from mcp_agent.agents.agent import Agent
from mcp_agent.config import Settings
from mcp_agent.logging.events import EventType
from mcp_agent.logging.listeners import EventListener
from mcp_agent.logging.logger import get_logger

logger = get_logger(__name__)


class FastAgent:
    """A simple agent implementation for fast-agent."""

    def __init__(
        self,
        model: Optional[str] = None,
        settings: Optional[Settings] = None,
        config_path: Optional[str] = None,
    ):
        """Initialize a FastAgent instance.

        Args:
            model: Optional model to use for the agent
            settings: Optional settings to use for the agent
            config_path: Optional path to a config file
        """
        self.model = model
        self.settings = settings
        self.config_path = config_path
        self._event_listeners: List[EventListener] = []
        self._logger = logger

    def add_event_listener(self, listener: EventListener) -> None:
        """Add an event listener to the agent.

        Args:
            listener: The event listener to add
        """
        self._event_listeners.append(listener)

    def remove_event_listener(self, listener: EventListener) -> None:
        """Remove an event listener from the agent.

        Args:
            listener: The event listener to remove
        """
        if listener in self._event_listeners:
            self._event_listeners.remove(listener)

    async def _emit_event(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Emit an event to all registered listeners.

        Args:
            event_type: The type of event to emit
            data: The data to include with the event
        """
        for listener in self._event_listeners:
            try:
                await listener.on_event(event_type, data)
            except Exception as e:
                self._logger.error(f"Error in event listener: {e}")

    async def run(self, prompt: str) -> str:
        """Run the agent with the given prompt.

        Args:
            prompt: The prompt to send to the agent

        Returns:
            The agent's response
        """
        # Create an agent instance
        agent = Agent(model=self.model, settings=self.settings, config_path=self.config_path)

        # Emit starting event
        await self._emit_event(
            EventType.AGENT_START,
            {"prompt": prompt, "model": self.model or "default"}
        )

        try:
            # Run the agent
            response = await agent.run(prompt)

            # Emit completion event
            await self._emit_event(
                EventType.AGENT_COMPLETE,
                {"response": response}
            )

            return response
        except Exception as e:
            # Emit error event
            await self._emit_event(
                EventType.ERROR,
                {"error": str(e)}
            )
            raise
