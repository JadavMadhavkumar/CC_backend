#!/bin/bash
# Script to push code to GitHub - Run this on your local machine
# Save this as push_to_github.sh and run: bash push_to_github.sh

set -e

echo "=========================================="
echo "Carbon Credit Backend - GitHub Push Script"
echo "=========================================="

# Configuration
REPO_URL="https://github.com/JadavMadhavkumar/carbon_credit.git"
BRANCH="python-backend"
FOLDER="backend"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Error: Git is not installed. Please install git first."
    exit 1
fi

# Navigate to the backend folder
cd "$(dirname "$0")/.."

echo "Step 1: Initializing git repository..."
git init

echo "Step 2: Creating .gitignore if not exists..."
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.eggs/

# Virtual environments
venv/
ENV/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp

# Environment
.env
.env.local

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db

# Celery
celerybeat-schedule
celerybeat.pid
EOF
fi

echo "Step 3: Staging all files..."
git add -A

echo "Step 4: Committing files..."
git commit -m "feat: Complete Carbon Credit Platform Backend

- FastAPI backend with async SQLAlchemy
- Carbon calculation formula engine (plastic waste, biochar, agricultural waste)
- JWT authentication with RBAC
- PostgreSQL database with 9 models
- Docker & Kubernetes support
- GitHub Actions CI/CD pipeline
- Rate limiting and security middleware
- Unit and integration tests"

echo "Step 5: Adding remote repository..."
git remote add origin $REPO_URL

echo "Step 6: Creating and switching to branch: $BRANCH"
git checkout -b $BRANCH

echo "Step 7: Pushing to GitHub..."
git push -u origin $BRANCH

echo ""
echo "=========================================="
echo "SUCCESS! Code pushed to GitHub"
echo "Branch: $BRANCH"
echo "URL: $REPO_URL"
echo "=========================================="
echo ""
echo "To enable CI/CD:"
echo "1. Go to GitHub repository"
echo "2. Navigate to Settings > Secrets"
echo "3. Add your database credentials as secrets"
echo "4. The CI/CD workflow will run automatically"
echo ""