#!/bin/bash
cd /home/trilok-lowanshi/LeetCodeNotionProject
echo "=== Sync started at $(date) ===" >> /home/trilok-lowanshi/LeetCodeNotionProject/sync.log
/home/trilok-lowanshi/LeetCodeNotionProject/venv/bin/python /home/trilok-lowanshi/LeetCodeNotionProject/sync.py >> /home/trilok-lowanshi/LeetCodeNotionProject/sync.log 2>&1
echo "=== Sync completed at $(date) ===" >> /home/trilok-lowanshi/LeetCodeNotionProject/sync.log
echo "" >> /home/trilok-lowanshi/LeetCodeNotionProject/sync.log
