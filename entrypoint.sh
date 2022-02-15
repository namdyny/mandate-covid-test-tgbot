#!/bin/bash
cd /home/ubuntu/projects/lilony-tgbot
echo "In lilony-tgbot"
source env/bin/activate
cd app/
nohup python main.py &

