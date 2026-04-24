#!/bin/bash
# Trelo Labs VDC Document Intelligence - Quick Start

echo "=================================="
echo "Trelo Labs VDC Document Intelligence"
echo "=================================="
echo ""

# Check if backend is already running
if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    echo "Backend is already running on port 5001"
else
    echo "Starting backend on port 5001..."
    python3 backend/app.py > backend.log 2>&1 &
    sleep 10
    if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
        echo "Backend is up!"
    else
        echo "Backend failed to start. Check backend.log"
        exit 1
    fi
fi

echo ""
echo "Seeding demo data..."
python3 seed_demo.py

echo ""
echo "Starting frontend server on port 8080..."
cd frontend && python3 -m http.server 8080 > ../frontend.log 2>&1 &
echo "Frontend is up!"

echo ""
echo "=================================="
echo "VDC Document Intelligence is LIVE"
echo "=================================="
echo "Backend:  http://localhost:5001"
echo "Frontend: http://localhost:8080"
echo ""
echo "Open your browser to http://localhost:8080"
echo ""
