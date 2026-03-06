@echo off
REM Pharmly Startup Script (Windows)
REM Starts both backend and frontend

echo.
echo 🚀 Starting Pharmly...
echo.

REM Check if we're in the right directory
if not exist "backend\run.py" (
    echo ❌ Error: backend\run.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Start backend
echo 📦 Starting backend server...
start "Pharmly Backend" /d backend python run.py
timeout /t 2 /nobreak

echo ✅ Backend started on http://localhost:5000
echo.

REM Start frontend
echo 🎨 Starting frontend server...
cd Frontend
start "Pharmly Frontend" python -m http.server 8000
timeout /t 1 /nobreak
cd ..

echo ✅ Frontend started on http://localhost:8000
echo.
echo 🎉 Pharmly is running!
echo.
echo 📍 Access the application:
echo    Frontend: http://localhost:8000/html/index.html
echo    Backend API: http://localhost:5000/health
echo.
echo ⚠️  Close the terminal windows to stop the servers
echo.
pause
