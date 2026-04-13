#!/bin/bash
# Intel Swarm Cron Trigger
# Runs at 9AM, 3PM, 9PM SGT (1:00, 7:00, 13:00 UTC)
# Cron: 0 1,7,13 * * * cd /home/yeoel/.openclaw/workspace && python intel_swarm_orchestrator.py

cd "$(dirname "$0")"

echo "[$(date)] Intel Swarm starting..."
python intel_swarm_orchestrator.py 2>&1 | tee -a intel_swarm/intel_swarm.log
echo "[$(date)] Intel Swarm done."
