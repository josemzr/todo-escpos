#!/usr/bin/env python3
"""
Deprecated CLI for task generation - now use the web application instead.

Please use the new web application by running:
    python app.py

Then visit http://localhost:5000 in your web browser for the full todo manager.
"""

import sys

def main():
    """Main CLI entry point - redirects to web application."""
    print("=" * 60)
    print("TODO MANAGER - WEB APPLICATION")
    print("=" * 60)
    print()
    print("This CLI tool has been replaced by a web application.")
    print()
    print("To use the new Todo Manager:")
    print("1. Run: python app.py")
    print("2. Open http://localhost:5000 in your web browser")
    print("3. Create and manage tasks with thermal printer integration")
    print()
    print("Features:")
    print("- Web-based task creation and management")
    print("- Database persistence")
    print("- Thermal printer integration (Ethernet: 172.31.23.129)")
    print("- Responsive mobile-friendly interface")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
