#!/bin/bash
# Intel Swarm Trigger — invoked by cron
cd /home/yeoel/.openclaw/workspace
python3 intel_swarm_prep.py 2>&1
