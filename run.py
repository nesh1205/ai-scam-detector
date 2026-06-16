#!/usr/bin/env python3
"""
AI Scam Detector - Quick Start Script
Run this to start the Flask app
"""

import subprocess
import sys
import os


def main():
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("\n" + "=" * 50)
    print("  AI Scam Detector - Starting Application")
    print("=" * 50 + "\n")

    # Run Flask app
    cmd = [sys.executable, "app.py"]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
