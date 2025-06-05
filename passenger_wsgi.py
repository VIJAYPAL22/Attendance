#!/usr/bin/python3
import sys
import os

# Add your project directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Import your Flask app from run.py
from run import app as application

if __name__ == "__main__":
    application.run()
