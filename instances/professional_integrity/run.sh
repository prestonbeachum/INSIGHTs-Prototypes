#!/bin/bash
# Launch script for Professional Integrity SIM-U application

cd "$(dirname "$0")"
source ../../.venv/bin/activate
streamlit run streamlit_app.py --server.port 8501

