"""Web application for fast-agent GUI."""

import asyncio
import os
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from mcp_agent.config import Settings
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.gui.websocket_manager import WebSocketManager
from mcp_agent.logging.events import EventType
from mcp_agent.logging.listeners import EventListener

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

class WebUIEventListener(EventListener):
    """Event listener that forwards events to WebSocket clients."""
    
    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
        
    async def on_event(self, event_type: EventType, data: dict):
        """Forward events to WebSocket clients."""
        await self.ws_manager.broadcast({
            "type": event_type.value,
            "data": data
        })

def create_app(settings: Optional[Settings] = None) -> FastAPI:
    """Create a FastAPI application for the GUI."""
    app = FastAPI(title="Fast-Agent GUI")
    
    # Mount static files
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    
    # Setup templates
    templates = Jinja2Templates(directory=TEMPLATES_DIR)
    
    # WebSocket manager for real-time updates
    ws_manager = WebSocketManager()
    
    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """Render the main page."""
        return templates.TemplateResponse(
            "index.html", 
            {"request": request}
        )
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates."""
        await ws_manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_json()
                if data["type"] == "run_agent":
                    # Run agent in background task
                    asyncio.create_task(run_agent(data["prompt"], data["model"], ws_manager))
                elif data["type"] == "stop_agent":
                    # TODO: Implement agent stopping
                    pass
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)
    
    async def run_agent(prompt: str, model: str, ws_manager: WebSocketManager):
        """Run an agent with the given prompt and model."""
        try:
            # Create a FastAgent instance
            agent = FastAgent(model=model)
            
            # Add WebSocket event listener
            agent.add_event_listener(WebUIEventListener(ws_manager))
            
            # Run the agent
            response = await agent.run(prompt)
            
            # Send the final response
            await ws_manager.broadcast({
                "type": "agent_response",
                "data": {
                    "response": response
                }
            })
        except Exception as e:
            # Send error message
            await ws_manager.broadcast({
                "type": "error",
                "data": {
                    "message": str(e)
                }
            })
    
    @app.get("/models")
    async def get_models():
        """Get available models."""
        # This is a placeholder - in a real implementation, we would get this from the config
        return {
            "models": [
                "gpt-4o",
                "gpt-4-turbo",
                "claude-3-opus",
                "claude-3-sonnet",
                "claude-3-haiku"
            ]
        }
    
    return app

def run_gui(host: str = "127.0.0.1", port: int = 8000, settings: Optional[Settings] = None):
    """Run the GUI server."""
    app = create_app(settings)
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_gui()
