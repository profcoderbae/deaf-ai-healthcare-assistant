#!/usr/bin/env python3
"""
Field Trial Analytics Dashboard — Launcher
===========================================
Generates sample data (if needed) and launches the Streamlit dashboard.

Usage:
    python run_dashboard.py              # Generate data + launch
    python run_dashboard.py --data-only  # Generate data only
    streamlit run src/dashboard.py       # Launch dashboard directly
"""

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.data_loader import generate_dashboard_data


def main():
    parser = argparse.ArgumentParser(description="Field Trial Analytics Dashboard")
    parser.add_argument("--data-only", action="store_true",
                       help="Only generate data, don't launch dashboard")
    args = parser.parse_args()
    
    # Generate data if needed
    if not os.path.exists("data/mango_trial_data.csv"):
        print("Generating sample trial data...")
        generate_dashboard_data()
        print()
    
    if args.data_only:
        print("Data generation complete.")
        return
    
    # Launch Streamlit
    print("Launching Streamlit dashboard...")
    print("Open http://localhost:8501 in your browser")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "src/dashboard.py",
        "--server.port", "8501",
    ])


if __name__ == "__main__":
    main()
