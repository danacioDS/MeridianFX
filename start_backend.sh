#!/bin/bash
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:${PWD}"
pkill -9 -f uvicorn || true
sudo fuser -k 8000/tcp 2>/dev/null || true
sleep 2
uvicorn backend.layer1.main:app --reload --host 0.0.0.0 --port 8000
