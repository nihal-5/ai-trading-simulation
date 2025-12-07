#!/bin/bash
# Launch script for AI Trading Dashboard

echo "🚀 Starting AI Trading Dashboard..."
echo ""
echo "Dashboard will be available at:"
echo "  http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

cd "$(dirname "$0")"
python dashboard.py
