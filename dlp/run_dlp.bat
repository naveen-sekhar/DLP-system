@echo off
cd /d %~dp0
start cmd /k mitmdump -s mitm_script.py --mode transparent --listen-port 8080
