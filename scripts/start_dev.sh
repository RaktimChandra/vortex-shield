#!/bin/bash
# Development startup script for VORTEX Shield 2.0

echo "=========================================="
echo "VORTEX Shield 2.0 - Development Setup"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

echo ""
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt

echo ""
echo "📦 Installing frontend dependencies..."
cd ../frontend
npm install

echo ""
echo "🤖 Training AI models..."
cd ../backend
python -m app.ai.model_trainer

echo ""
echo "🗄️  Initializing database..."
python app/scripts/init_database.py

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  Backend:  cd backend && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "Access at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "=========================================="
