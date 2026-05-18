#!/bin/bash
# ============================================
# Carbon Credit Platform - GitHub Push Script
# ============================================
# Run this script to push the code to GitHub
# ============================================

set -e

REPO_URL="https://github.com/JadavMadhavkumar/carbon_credit.git"
BRANCH="python-backend"

echo "================================================"
echo "  Carbon Credit Platform - Push to GitHub"
echo "================================================"

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

cd "$BACKEND_DIR"

echo ""
echo "Step 1: Checking git installation..."
if ! command -v git &> /dev/null; then
    echo "ERROR: Git is not installed"
    echo "Install git: https://git-scm.com/downloads"
    exit 1
fi

echo "Step 2: Initializing git repository..."
git init

echo "Step 3: Configuring git user..."
git config user.email "github-actions[bot]@users.noreply.github.com"
git config user.name "GitHub Actions"

echo "Step 4: Creating .gitignore..."
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

# OS
.DS_Store

# Celery
celerybeat-*

# Git
.gitignore
EOF

echo "Step 5: Adding files..."
git add -A

echo "Step 6: Committing changes..."
git commit -m "feat: Complete Carbon Credit Platform Backend

- FastAPI async backend with SQLAlchemy 2.0
- Carbon calculation formula engine (plastic waste, agricultural waste, biochar)
- JWT authentication with RBAC
- PostgreSQL database with complete models
- Docker & Docker Compose support
- Kubernetes manifests
- GitHub Actions CI/CD pipeline
- Rate limiting and security middleware
- Unit & integration tests"

echo "Step 7: Adding remote..."
git remote add origin "$REPO_URL"

echo "Step 8: Creating branch '$BRANCH'..."
git branch -M "$BRANCH"

echo "Step 9: Pushing to GitHub..."
git push -u origin "$BRANCH"

echo ""
echo "================================================"
echo "  SUCCESS! Code pushed to GitHub!"
echo "================================================"
echo ""
echo "Repository: $REPO_URL"
echo "Branch: $BRANCH"
echo ""
echo "Next steps:"
echo "1. Go to GitHub repository"
echo "2. Create a Pull Request from 'python-backend' to 'main'"
echo "3. CI/CD will run automatically"
echo ""
echo "To add secrets (optional):"
echo "Settings > Secrets and variables > Actions"
echo "  - DATABASE_URL"
echo "  - REDIS_URL"
echo "  - SECRET_KEY"
echo ""