#!/bin/bash
# Script to run the Airbnb Photo Enhancer application

cd "/Users/vahagn/Desktop/Ai Agents/airbnb_photoh_enhancment"
source venv/bin/activate

# Kill any existing process on port 5000
lsof -ti:5000 | xargs kill -9 2>/dev/null || true

# Run the Flask application
python app.py

