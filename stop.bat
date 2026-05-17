@echo off
title Xiaoman Stop

echo Stopping xiaoman backend...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1 && echo Killed PID %%a
)

echo Done.
pause
