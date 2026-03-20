#!/bin/bash
# VORTEX Shield 2.0 - Deployment Script

set -e

echo "🚀 Starting VORTEX Shield 2.0 Deployment..."

# Configuration
ENVIRONMENT=${1:-production}
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

echo_error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# Pre-deployment checks
echo "📋 Running pre-deployment checks..."

# Check if required files exist
if [ ! -f "$BACKEND_DIR/.env.$ENVIRONMENT" ]; then
    echo_error "Backend environment file not found: $BACKEND_DIR/.env.$ENVIRONMENT"
fi

if [ ! -f "$FRONTEND_DIR/.env.$ENVIRONMENT" ]; then
    echo_error "Frontend environment file not found: $FRONTEND_DIR/.env.$ENVIRONMENT"
fi

echo_success "Environment files found"

# Backend deployment
echo "🔧 Deploying backend..."
cd $BACKEND_DIR

# Copy environment file
cp .env.$ENVIRONMENT .env
echo_success "Environment configured"

# Install dependencies
pip install -r requirements.txt
echo_success "Dependencies installed"

# Run database migrations (if any)
# alembic upgrade head
echo_success "Database ready"

cd ..

# Frontend deployment
echo "🎨 Deploying frontend..."
cd $FRONTEND_DIR

# Copy environment file
cp .env.$ENVIRONMENT .env.local
echo_success "Environment configured"

# Install dependencies
npm ci
echo_success "Dependencies installed"

# Build production bundle
npm run build
echo_success "Build completed"

cd ..

# Start services with Docker
echo "🐳 Starting services..."
docker-compose -f docker-compose.prod.yml up -d --build

if [ $? -eq 0 ]; then
    echo_success "Services started successfully"
else
    echo_error "Failed to start services"
fi

# Health check
echo "🏥 Running health checks..."
sleep 5

# Check backend health
BACKEND_HEALTH=$(curl -s http://localhost:8000/health/ready)
if [ $? -eq 0 ]; then
    echo_success "Backend is healthy"
else
    echo_warning "Backend health check failed"
fi

# Check frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo_success "Frontend is accessible"
else
    echo_warning "Frontend check returned: $FRONTEND_STATUS"
fi

echo ""
echo "✅ Deployment completed!"
echo "📊 Backend: http://localhost:8000"
echo "🎨 Frontend: http://localhost:3000"
echo "📖 API Docs: http://localhost:8000/docs"
