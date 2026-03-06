#!/bin/bash

# Pharmly Startup Script
# Starts both backend and frontend

echo "🚀 Starting Pharmly..."

# Check if we're in the right directory
if [ ! -f "backend/run.py" ]; then
    echo "❌ Error: backend/run.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Start backend
echo "📦 Starting backend server..."
cd backend
python run.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

echo "✅ Backend running (PID: $BACKEND_PID) on http://localhost:5000"

# Start frontend server
echo "🎨 Starting frontend server..."
cd ../Frontend
python -m http.server 8000 &
FRONTEND_PID=$!

sleep 1

if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start"
    kill $BACKEND_PID
    exit 1
fi

echo "✅ Frontend running (PID: $FRONTEND_PID) on http://localhost:8000"
echo ""
echo "🎉 Pharmly is running!"
echo ""
echo "📍 Access the application:"
echo "   Frontend: http://localhost:8000/html/index.html"
echo "   Backend API: http://localhost:5000/health"
echo ""
echo "⚠️  Press Ctrl+C to stop both servers"
echo ""

# Handle Ctrl+C
trap "
    echo '🛑 Stopping servers...'
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
" SIGINT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
