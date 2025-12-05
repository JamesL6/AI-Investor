# Setup Guide - Environment Variables

## Local Development Setup

### Step 1: Create `.env` file

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your actual API keys:
   ```bash
   XAI_API_KEY=your_actual_xai_api_key_here
   GOOGLE_API_KEY=your_actual_google_api_key_here  # Optional
   ```

**Important:** The `.env` file is already in `.gitignore` and will **NOT** be committed to GitHub.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run Locally

```bash
streamlit run app.py
```

The app will automatically load environment variables from `.env`.

---

## Railway Deployment Setup

### Step 1: Push Code to GitHub

Make sure your code is pushed to GitHub (without `.env` file - it's in `.gitignore`).

### Step 2: Connect Railway to GitHub

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Select your repository

### Step 3: Add Environment Variables in Railway

1. In Railway dashboard → Click your service
2. Go to **"Variables"** tab
3. Click **"New Variable"** or use **"Raw Editor"**
4. Add:
   ```
   XAI_API_KEY=your_actual_xai_api_key_here
   ```
5. Click **"Save"**

Railway will automatically redeploy with the new environment variable.

### Step 4: Get Your Public URL

1. Railway dashboard → Settings
2. Scroll to "Networking"
3. Click "Generate Domain"
4. Your app is live!

---

## Security Notes

✅ **DO:**
- Use `.env` file for local development
- Add environment variables in Railway dashboard
- Keep `.env` in `.gitignore` (already done)
- Use `.env.example` as a template (without real keys)

❌ **DON'T:**
- Commit `.env` file to GitHub
- Put API keys in code files
- Put API keys in documentation
- Share your `.env` file

---

## Troubleshooting

**"API key not found" error:**
- Check that `.env` file exists locally
- Verify `XAI_API_KEY` is set in Railway Variables
- Make sure `.env` is in `.gitignore` (it should be)

**"Module not found: dotenv":**
- Run: `pip install python-dotenv`
- Or: `pip install -r requirements.txt`

---

Your API keys are now secure! 🔒

