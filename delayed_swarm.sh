#!/bin/bash
# Delayed Intel Swarm — runs in 1 hour
# Log output
LOG="/home/yeoel/.openclaw/workspace/intel_swarm/scratch/delayed_swarm.log
exec >> "$LOG" 2>&1
echo "[$(date)] Delayed swarm starting in 1 hour..."
sleep 3600
echo "[$(date)] 1 hour elapsed. Running prep..."
cd /home/yeoel/.openclaw/workspace
python3 intel_swarm_prep.py
echo "[$(date)] Prep done. Awaiting orchestrator..."
