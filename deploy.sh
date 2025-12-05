#!/bin/bash
# Quick deployment script for Graham & Buffett Investor Agent

echo "🚀 Preparing for deployment..."
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git repository already exists"
fi

# Check if .gitignore exists
if [ ! -f ".gitignore" ]; then
    echo "⚠️  Warning: .gitignore not found"
fi

echo ""
echo "📝 Next steps:"
echo ""
echo "1. Create a new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Name it: benjamin-graham-ai (or your preferred name)"
echo "   - Don't initialize with README"
echo ""
echo "2. Add and commit your code:"
echo "   git add ."
echo "   git commit -m 'Initial commit - Graham & Buffett Investor Agent'"
echo ""
echo "3. Connect to GitHub (replace YOUR_USERNAME):"
echo "   git remote add origin https://github.com/YOUR_USERNAME/benjamin-graham-ai.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. Deploy on Streamlit Cloud:"
echo "   - Go to https://share.streamlit.io"
echo "   - Sign in with GitHub"
echo "   - Click 'New app'"
echo "   - Select your repository"
echo "   - Main file: app.py"
echo "   - Python version: 3.11"
echo ""
echo "5. Add API key in Streamlit Cloud:"
echo "   - Settings → Secrets"
echo "   - Add: XAI_API_KEY=your_xai_api_key_here"
echo ""
echo "✅ Your app will be live at: https://YOUR-APP-NAME.streamlit.app"
echo ""

