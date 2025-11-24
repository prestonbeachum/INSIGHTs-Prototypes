#!/bin/bash
# Launch script for INSIGHTs Admin Dashboard

cd "$(dirname "$0")/.."

echo "Starting INSIGHTs Admin Dashboard..."
echo "Admin panel will be available at: http://localhost:8500"

# Activate virtual environment and run admin app
source .venv/bin/activate && streamlit run admin/admin_app.py --server.port 8500
