#!/bin/bash
# Railway Deployment Helper Script

echo "🚀 Railway Deployment Setup"
echo "=========================="

echo "1. Setting up Git repository..."
git init
git add .
git commit -m "Cricket bot ready for Railway deployment"

echo ""
echo "📋 NEXT STEPS:"
echo "1. Create MongoDB Atlas cluster (5 min): https://mongodb.com/atlas"
echo "2. Update .env with Atlas connection string"
echo "3. Create GitHub repo and push code:"
echo "   git remote add origin https://github.com/YOURUSERNAME/matchbot.git"
echo "   git push -u origin main"
echo "4. Deploy on Railway: https://railway.app"
echo "   - Connect GitHub repo"
echo "   - Add environment variables from .env"
echo "   - Deploy!"

echo ""
echo "✅ Current status:"
echo "   - Bot code: Ready"
echo "   - Database: LOCAL (needs Atlas for Railway)"
echo "   - Git: Initialized"

echo ""
echo "🎯 After deployment, your bot will be online 24/7!"