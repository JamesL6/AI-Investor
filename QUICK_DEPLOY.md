# Quick Deploy Guide - Get Your App Live in 5 Minutes! 🚀

## Step-by-Step: Deploy to Streamlit Cloud (FREE)

### Step 1: Create GitHub Repository

1. Go to **https://github.com/new**
2. Repository name: `benjamin-graham-ai` (or your choice)
3. Description: "Graham & Buffett Intelligent Investor Agent"
4. **Make it Public** (required for free Streamlit Cloud)
5. **DO NOT** check "Initialize with README"
6. Click **"Create repository"**

### Step 2: Push Code to GitHub

Run these commands in your terminal:

```bash
cd "/Users/jameslarosa/Benjamin Graham AI"

# Commit your code
git add .
git commit -m "Initial commit - Graham & Buffett Investor Agent"

# Connect to GitHub (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/benjamin-graham-ai.git
git branch -M main
git push -u origin main
```

**Note:** You'll need to authenticate with GitHub (use a personal access token if prompted).

### Step 3: Deploy on Streamlit Cloud

1. Go to **https://share.streamlit.io**
2. Click **"Sign in"** → Sign in with **GitHub**
3. Click **"New app"**
4. Fill in:
   - **Repository**: Select `YOUR_USERNAME/benjamin-graham-ai`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **Python version**: `3.11` or `3.12`
5. Click **"Deploy"**

### Step 4: Add API Key (CRITICAL!)

1. In Streamlit Cloud, click **"Settings"** (⚙️ icon)
2. Click **"Secrets"**
3. Add this:

```toml
XAI_API_KEY = "your_xai_api_key_here"
```

4. Click **"Save"**
5. The app will automatically redeploy

### Step 5: Access Your Live App! 🎉

Your app will be live at:
**`https://YOUR-APP-NAME.streamlit.app`**

---

## Alternative: Deploy to Railway (You Already Use This)

If you prefer Railway:

```bash
# Install Railway CLI (if not already)
npm i -g @railway/cli

# Login
railway login

# Initialize project
cd "/Users/jameslarosa/Benjamin Graham AI"
railway init

# Set API key
railway variables set XAI_API_KEY=your_xai_api_key_here

# Deploy
railway up

# Get public URL
railway domain
```

---

## Troubleshooting

**"App won't start"**
- Check that `app.py` is in the root directory ✅
- Verify `requirements.txt` has all dependencies ✅
- Check Streamlit Cloud logs for errors

**"API calls failing"**
- Verify `XAI_API_KEY` is set in Secrets
- Check API key is correct (no extra spaces)

**"Module not found"**
- Ensure all dependencies are in `requirements.txt`
- Streamlit Cloud will auto-install from requirements.txt

---

## What Gets Deployed

✅ All your code (`src/`, `app.py`)  
✅ Requirements (`requirements.txt`)  
✅ Configuration (`.streamlit/config.toml`)  
❌ **NOT** your API keys (they're in Secrets)  
❌ **NOT** your local files (`.gitignore` protects them)

---

## After Deployment

- **Auto-deploy**: Every `git push` to main branch auto-deploys
- **Custom domain**: Streamlit Cloud Pro allows custom domains
- **Monitoring**: Check logs in Streamlit Cloud dashboard
- **Updates**: Just `git push` to update the live app!

---

**Need help?** Check `DEPLOYMENT.md` for detailed instructions.

