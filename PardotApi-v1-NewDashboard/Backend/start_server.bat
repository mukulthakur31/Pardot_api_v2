@echo off
echo ========================================
echo Pardot API Server Startup
echo ========================================

echo.
echo 1. Checking Redis connection...
python check_redis.py
if %errorlevel% neq 0 (
    echo WARNING: Redis check failed - continuing without cache
    echo.
)

echo.
echo 2. Starting Pardot API Server...
echo Press Ctrl+C to stop the server
echo.

python start_server.py

echo.
echo Server stopped.
pause