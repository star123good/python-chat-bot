#!/bin/sh
clear
sudo timedatectl set-timezone Europe/London
sudo hwclock --show
cd chat_bot
nohup python3 ICQ_Bot.py & nohup python3 ICQ_Thread.py & nohup python3 api_service.py &