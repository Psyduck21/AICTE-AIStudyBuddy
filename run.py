#!/usr/bin/env python3
"""Entry point for AI Study Buddy Pro"""
import os
import sys
import subprocess

def main():
    """Launch the Streamlit application"""
    # Add src directory to Python path
    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    sys.path.append(os.path.dirname(src_path))
    
    # Get the path to app.py
    app_path = os.path.join(src_path, "app.py")
    
    # Launch Streamlit
    print("Starting AI Study Buddy Pro...")
    print("Loading interface in your browser...")
    subprocess.run(["streamlit", "run", app_path], check=True)

if __name__ == "__main__":
    main()