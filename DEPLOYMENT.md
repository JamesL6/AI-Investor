# Deployment Guide - Benjamin Graham Investor Agent

This guide covers deploying the Streamlit app to make it accessible via URL.

## Option 1: Streamlit Cloud (Recommended - Easiest & Free)

Streamlit Cloud is the easiest way to deploy Streamlit apps for free.

### Steps:

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Go to [share.streamlit.io](https://share.streamlit.io)**
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set Main file path: `app.py`
   - Set Python version: `3.11` or `3.12`

3. **Add Environment Variables**
   - In Streamlit Cloud dashboard, go to "Settings" → "Secrets"
   - Add:
     ```
     XAI_API_KEY=your_xai_api_key_here
     ```
   - (Optional) Add Google API key if using Gemini:
     ```
     GOOGLE_API_KEY=your_google_api_key
     ```

4. **Deploy**
   - Click "Deploy"
   - Your app will be live at: `https://YOUR-APP-NAME.streamlit.app`

### Pros:
- ✅ Free
- ✅ Automatic deployments on git push
- ✅ Built-in HTTPS
- ✅ Easy environment variable management

---

## Option 2: Railway (You Already Use This)

Railway is great for production apps with more control.

### Steps:

1. **Install Railway CLI** (if not already installed)
   ```bash
   npm i -g @railway/cli
   ```

2. **Create railway.json** (already created)
   ```bash
   railway login
   railway init
   ```

3. **Set Environment Variables**
   ```bash
   railway variables set XAI_API_KEY=your_xai_api_key_here
   ```

4. **Deploy**
   ```bash
   railway up
   ```

5. **Generate Public URL**
   ```bash
   railway domain
   ```

### Pros:
- ✅ More control
- ✅ Custom domains
- ✅ Better for production
- ✅ You're already familiar with it

---

## Option 3: Render (Free Tier Available)

1. **Go to [render.com](https://render.com)**
2. **Create New Web Service**
3. **Connect GitHub repository**
4. **Configure:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - Environment: Python 3
5. **Add Environment Variables** in dashboard
6. **Deploy**

---

## Environment Variables Needed

Make sure these are set in your deployment platform:

- `XAI_API_KEY` - Required for Grok AI model
- `GOOGLE_API_KEY` - Optional, only if using Gemini models

---

## Testing Locally Before Deploying

```bash
# Test that everything works
export XAI_API_KEY="your_key_here"
streamlit run app.py
```

---

## Troubleshooting

### App won't start
- Check that `app.py` is in the root directory
- Verify `requirements.txt` includes all dependencies
- Check logs for missing environment variables

### API calls failing
- Verify API keys are set correctly
- Check rate limits on xAI/Google APIs
- Ensure network access is allowed

### Slow performance
- Consider reducing parallel workers in UI
- Add caching for frequently accessed stocks
- Use faster AI models (Grok Fast vs regular)

