#!/bin/bash
apt-get update && apt-get install -y libgomp1
exec uvicorn app:app --host 0.0.0.0 --port $PORT
