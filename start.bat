@echo off
title Xiaoman Backend
cd /d "%~dp0backend"

REM 加载 .env 文件（如果存在）
if exist "%~dp0.env" (
    for /f "usebackq tokens=1,2 delims==" %%a in ("%~dp0.env") do (
        if "%%a"=="MYSQL_HOST" set "MYSQL_HOST=%%b"
        if "%%a"=="MYSQL_USER" set "MYSQL_USER=%%b"
        if "%%a"=="MYSQL_PASSWORD" set "MYSQL_PASSWORD=%%b"
        if "%%a"=="MYSQL_DATABASE" set "MYSQL_DATABASE=%%b"
        if "%%a"=="DEEPSEEK_API_KEY" set "DEEPSEEK_API_KEY=%%b"
        if "%%a"=="JWT_SECRET" set "JWT_SECRET=%%b"
    )
) else (
    echo [WARN] .env file not found, using default localhost values
    echo [INFO] Copy .env.example to .env and fill in your credentials
)

REM 默认值（.env 中未设置时使用）
if not defined MYSQL_HOST set MYSQL_HOST=127.0.0.1
if not defined MYSQL_USER set MYSQL_USER=root
if not defined MYSQL_PASSWORD set MYSQL_PASSWORD=
if not defined MYSQL_DATABASE set MYSQL_DATABASE=xiaoman
if not defined DEEPSEEK_API_KEY set DEEPSEEK_API_KEY=
if not defined JWT_SECRET set JWT_SECRET=

if "%DEEPSEEK_API_KEY%"=="" (
    echo [ERROR] DEEPSEEK_API_KEY is not set
    echo [INFO] Please create .env file from .env.example and set your API key
    pause
    exit /b 1
)

echo Checking MySQL service...
sc query MySQL | find "RUNNING" >nul
if errorlevel 1 (
    echo [ERROR] MySQL not running, please start MySQL first
    pause
    exit /b 1
)
echo MySQL is running.

echo Starting xiaoman backend at http://127.0.0.1:8000 ...
echo.
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
