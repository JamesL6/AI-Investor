# Railway + GitHub Setup (Easiest Method!)

Railway can connect directly to your GitHub repo and auto-deploy on every push!

## Quick Setup Steps

### Step 1: Push Code to GitHub

```bash
cd "/Users/jameslarosa/Benjamin Graham AI"

# Create GitHub repo first at https://github.com/new
# Then run:

git add .
git commit -m "Initial commit - Graham & Buffett Investor Agent"
git remote add origin https://github.com/YOUR_USERNAME/benjamin-graham-ai.git
git branch -M main
git push -u origin main
```

### Step 2: Connect Railway to GitHub

1. **Go to [railway.app](https://railway.app)**
2. **Sign in** (or create account)
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"** (or "GitHub Repo")
5. **Authorize Railway** to access your GitHub (if prompted)
6. **Select your repository**: `benjamin-graham-ai`
7. Railway will automatically:
   - Detect it's a Python app
   - Read `railway.json` for configuration
   - Start deploying!

### Step 3: Add Environment Variable (API Key)

1. In Railway dashboard, click on your **service** (the app name)
2. Go to **"Variables"** tab
3. Click **"New Variable"** or **"Raw Editor"**
4. Add:
   ```
   XAI_API_KEY=your_xai_api_key_here
   ```
5. Click **"Save"** or **"Add"**
6. Railway will automatically redeploy with the new variable

### Step 4: Get Your Public URL

1. In Railway dashboard, click **"Settings"** (or the service)
2. Scroll to **"Networking"** or **"Domains"**
3. Click **"Generate Domain"** (or use the auto-generated one)
4. Your app will be live at: `https://YOUR-APP-NAME.up.railway.app`

## That's It! 🎉

**Auto-Deploy**: Every time you push to GitHub:
```bash
git push
```

Railway automatically:
- ✅ Detects the push
- ✅ Pulls latest code
- ✅ Rebuilds and redeploys
- ✅ Your app updates live!

## Your Railway Configuration

Your `railway.json` is already set up correctly:
- ✅ Uses NIXPACKS builder (auto-detects Python)
- ✅ Starts Streamlit on `$PORT` (Railway sets this automatically)
- ✅ Binds to `0.0.0.0` (required for Railway)
- ✅ Headless mode enabled

## Troubleshooting

**"Deployment failed"**
- Check Railway logs: Dashboard → Service → "Deployments" → Click latest → "View Logs"
- Verify `XAI_API_KEY` is set in Variables tab
- Make sure `app.py` is in root directory

**"App won't start"**
- Check logs for errors
- Verify all dependencies in `requirements.txt`
- Railway auto-installs from `requirements.txt`

**"Can't connect to GitHub"**
- Make sure Railway has GitHub access (Settings → GitHub)
- Repository must be accessible to Railway

## Railway vs Streamlit Cloud

**Railway Advantages:**
- ✅ More control and customization
- ✅ Better for production apps
- ✅ Custom domains easier
- ✅ You're already familiar with it

**Streamlit Cloud Advantages:**
- ✅ Completely free (no credit limits)
- ✅ Optimized specifically for Streamlit
- ✅ Simpler setup

Both work great! Railway is perfect if you're already using it.

---

**Need help?** Check Railway logs - they're very detailed and helpful!

