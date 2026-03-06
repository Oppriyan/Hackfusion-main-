#!/bin/bash
# QUICK START SCRIPT FOR PHARMLY

echo "🏥 PHARMLY - Quick Start Setup"
echo "=============================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found"

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example backend/.env
    echo "⚠️  Please update backend/.env with your Azure OpenAI credentials"
    echo "   AZURE_OPENAI_API_KEY=your_key_here"
    echo "   AZURE_OPENAI_API_VERSION=2024-02-15"
    echo "   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/"
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
echo "✅ Backend dependencies installed"

# Check requirements
python -c "import flask; import openai; import pydantic; import langsmith"
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Re-running pip install..."
    pip install -r requirements.txt
fi

echo ""
echo "🎯 Ready to start!"
echo "===================="
echo ""
echo "To start the backend:"
echo "  cd backend"
echo "  python run.py"
echo ""
echo "To start the frontend:"
echo "  Open: Frontend/html/index.html in browser"
echo "  Or run: python -m http.server 8000"
echo ""
echo "Backend will run on: http://localhost:5000"
echo "Frontend will run on: http://localhost:8000"
echo ""
echo "✅ Setup complete!"
