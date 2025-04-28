#!/usr/bin/env python3
"""
Run the Fast-Agent GUI.

This script launches the graphical user interface for fast-agent.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_agent.gui.web_app import run_gui


def main():
    """Run the GUI."""
    print("Starting Fast-Agent GUI...")
    run_gui(host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
