@echo off
REM Development startup script for VORTEX Shield 2.0 (Windows)

echo ==========================================
echo VORTEX Shield 2.0 - Development Setup
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed
    exit /b 1
)

echo.
echo 📦 Installing backend dependencies...
cd backend
pip install -r requirements.txt

echo.
echo 📦 Installing frontend dependencies...
cd ..\frontend
call npm install

echo.
echo 🤖 Training AI models...
cd ..\backend
python -m app.ai.model_trainer

echo.
echo 🗄️  Initializing database...
python app\scripts\init_database.py

echo.
echo ==========================================
echo ✅ Setup Complete!
echo ==========================================
echo.
echo To start the application:
echo   Backend:  cd backend ^&^& uvicorn app.main:app --reload
echo   Frontend: cd frontend ^&^& npm run dev
echo.
echo Access at:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ==========================================
pause
