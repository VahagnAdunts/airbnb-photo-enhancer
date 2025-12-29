#!/bin/bash
# Script to push code to GitHub

echo "🚀 Pushing code to GitHub..."
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "❌ Git not initialized. Run: git init"
    exit 1
fi

# Get GitHub username and repo name
echo "Enter your GitHub username:"
read GITHUB_USERNAME

echo "Enter your repository name (e.g., airbnb-photo-enhancer):"
read REPO_NAME

# Remove old remote if exists
git remote remove origin 2>/dev/null

# Add new remote
echo ""
echo "Adding remote: https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Verify remote
echo ""
echo "Current remotes:"
git remote -v

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
echo "Note: You may be asked for GitHub credentials"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "📦 Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "Next steps:"
    echo "1. Go to Render dashboard"
    echo "2. Connect your repository: $REPO_NAME"
    echo "3. Continue with deployment"
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "   - Repository doesn't exist on GitHub (create it first)"
    echo "   - Authentication failed (use Personal Access Token)"
    echo "   - Wrong repository URL"
    echo ""
    echo "See PUSH_TO_GITHUB.md for detailed help"
fi

