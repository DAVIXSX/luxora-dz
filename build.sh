#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "🚀 Starting Luxora DZ build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 Creating necessary directories..."
mkdir -p static/uploads

echo "🗄️ Initializing database..."
python -c "
import os
from app import init_db
print('Initializing database tables...')
init_db()
print('Database initialization complete!')
"

echo "✅ Build process completed successfully!"
echo "🎉 Luxora DZ is ready for deployment!"
