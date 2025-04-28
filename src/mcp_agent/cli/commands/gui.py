"""GUI command for fast-agent CLI."""

import typer
from rich.console import Console

from mcp_agent.gui.web_app import run_gui

app = typer.Typer(help="Launch the graphical user interface for fast-agent")
console = Console()

@app.callback(invoke_without_command=True)
def main(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind the server to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind the server to"),
    open_browser: bool = typer.Option(True, "--open-browser/--no-open-browser", help="Open browser automatically"),
) -> None:
    """Launch the graphical user interface for fast-agent."""
    import webbrowser
    from threading import Timer
    
    console.print(f"[bold green]Starting Fast-Agent GUI on http://{host}:{port}[/bold green]")
    
    if open_browser:
        # Open browser after a short delay to ensure server is running
        def open_browser_tab():
            webbrowser.open(f"http://{host}:{port}")
        
        Timer(1.5, open_browser_tab).start()
    
    # Run the GUI server
    run_gui(host=host, port=port)
