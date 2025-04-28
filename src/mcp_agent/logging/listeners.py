"""
Event listeners for the logging system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from mcp_agent.logging.events import EventType


class EventListener(ABC):
    """Base class for event listeners."""
    
    @abstractmethod
    async def on_event(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Handle an event.
        
        Args:
            event_type: The type of event
            data: The data associated with the event
        """
        pass
