# Railway Deployment Guide (GitHub Integration)

Railway can connect directly to your GitHub repo and auto-deploy on every push!

## Step 1: Push Code to GitHub

First, make sure your code is on GitHub:

```bash
cd "/Users/jameslarosa/Benjamin Graham AI"

# If you haven't committed yet:
git add .
git commit -m "Initial commit - Graham & Buffett Investor Agent"

# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/benjamin-graham-ai.git
git branch -M main
git push -u origin main
```

## Step 2: Connect Railway to GitHub

1. **Go to [railway.app](https://railway.app)**
2. **Sign in** (or create account)
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. **Authorize Railway** to access your GitHub (if prompted)
6. **Select your repository**: `benjamin-graham-ai`
7. Railway will automatically detect it's a Python app

## Step 3: Configure Environment Variables

1. In Railway dashboard, click on your **service**
2. Go to **"Variables"** tab
3. Click **"New Variable"**
4. Add:
   - **Key**: `XAI_API_KEY`
   - **Value**: `your_xai_api_key_here`
5. Click **"Add"**

## Step 4: Railway Auto-Detects Configuration

Railway will automatically:
- ✅ Detect `requirements.txt` and install dependencies
- ✅ Use `railway.json` for build/start commands
- ✅ Deploy your app
- ✅ Generate a public URL

## Step 5: Get Your Public URL

1. In Railway dashboard, click **"Settings"**
2. Scroll to **"Networking"**
3. Click **"Generate Domain"** (or use the auto-generated one)
4. Your app will be live at: `https://YOUR-APP-NAME.up.railway.app`

## Auto-Deploy on Git Push

**That's it!** Now every time you push to GitHub:
```bash
git push
```

Railway will automatically:
1. Detect the push
2. Pull the latest code
3. Rebuild and redeploy
4. Your app updates live!

## Manual Deploy (if needed)

If you want to deploy manually via CLI:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project (if not already linked)
railway link

# Deploy
railway up
```

## Railway Configuration

Your `railway.json` is already configured:
- **Builder**: NIXPACKS (auto-detects Python)
- **Start Command**: Streamlit with proper port binding
- **Restart Policy**: Auto-restart on failure

## Troubleshooting

**"App won't start"**
- Check Railway logs: Dashboard → Service → "Deployments" → Click latest → "View Logs"
- Verify `XAI_API_KEY` is set in Variables
- Check that `app.py` is in root directory

**"Build failed"**
- Check `requirements.txt` has all dependencies
- Railway logs will show the exact error

**"Port binding error"**
- Railway automatically sets `$PORT` environment variable
- Your `railway.json` already handles this correctly

## Cost

- **Free tier**: $5/month credit (usually enough for small apps)
- **Hobby**: $5/month (if you exceed free tier)
- **Pro**: $20/month (for production apps)

Most small Streamlit apps stay within the free tier!

---

**That's it!** Railway + GitHub = Automatic deployments on every push! 🚀

