# 🚀 Complete Deployment Guide - Vercel + Railway

## Overview

- **Frontend (Next.js)** → Vercel
- **Backend (FastAPI)** → Railway or Render

---

## 📦 **Part 1: Deploy Backend to Railway**

### **Step 1: Create Railway Account**
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project"

### **Step 2: Deploy Backend**
1. Click "Deploy from GitHub repo"
2. Connect your GitHub account
3. Select your repository
4. Railway will auto-detect the project

### **Step 3: Configure Railway**
1. Click on your deployment
2. Go to "Settings" tab
3. Set these configurations:

**Root Directory:**
```
backend
```

**Install Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### **Step 4: Add Environment Variables**
1. Go to "Variables" tab
2. Click "New Variable"
3. Add all these from your `.env` file:

```
OPUS_API_KEY=your_opus_key
OPUS_BASE_URL=https://operator.opus.com
OPUS_WORKFLOW_ID=your_workflow_id
FIRECRAWL_API_KEY=your_firecrawl_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
RSS_FRESHNESS_DAYS=7
MAX_ARTICLES_PER_SOURCE=3
MAX_CRAWL_PAGES=3
DAILY_POST_LIMIT=40
MAX_ITEMS_PER_RUN=15
MIN_RELEVANCE_SCORE=0.5
USE_RSS_FEEDS=true
ENABLE_URL_DEDUPLICATION=true
TRACK_CREDIT_USAGE=true
```

### **Step 5: Deploy!**
1. Railway will automatically deploy
2. Wait for deployment to complete (2-3 minutes)
3. Copy your backend URL from Railway dashboard
   - Example: `https://your-app.up.railway.app`

---

## 🌐 **Part 2: Deploy Frontend to Vercel**

### **Option A: Deploy via Vercel Dashboard (Easiest)**

#### **Step 1: Push to GitHub**
```bash
# Make sure your code is on GitHub
cd /Users/anas/Documents/Ops\ on\ Opus/Content\ Automation

# Initialize git if not already done
git init
git add .
git commit -m "Ready for deployment"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

#### **Step 2: Deploy on Vercel**
1. Go to https://vercel.com
2. Sign up/Login with GitHub
3. Click "Add New Project"
4. Import your GitHub repository
5. Configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

#### **Step 3: Add Environment Variable**
1. In project settings → Environment Variables
2. Add this variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
   ```
   (Use the URL from Railway Step 5)

3. Click "Deploy"

#### **Step 4: Done!**
Your app will be live at: `https://your-project.vercel.app`

---

### **Option B: Deploy via Vercel CLI (Faster)**

#### **Step 1: Install Vercel CLI**
```bash
npm install -g vercel
```

#### **Step 2: Login**
```bash
vercel login
```

#### **Step 3: Deploy**
```bash
cd frontend

# First deployment (setup)
vercel

# Answer prompts:
# ✓ Set up and deploy: Yes
# ✓ Which scope: (your account)
# ✓ Link to existing project: No
# ✓ Project name: content-automation
# ✓ Directory: ./
# ✓ Override settings: No
```

#### **Step 4: Add Environment Variable**
```bash
# Add production environment variable
vercel env add NEXT_PUBLIC_API_URL production

# When prompted, enter:
https://your-railway-app.up.railway.app
```

#### **Step 5: Deploy to Production**
```bash
vercel --prod
```

#### **Step 6: Done!**
Your app is live! Vercel will show you the URL.

---

## 🔄 **Part 3: Update Railway CORS**

Since your frontend is now on a different domain, update the backend CORS:

1. Go to Railway dashboard
2. Add environment variable:
   ```
   FRONTEND_URL=https://your-project.vercel.app
   ```

3. Railway will auto-redeploy

---

## ✅ **Verification Checklist**

### **Backend (Railway)**
- [ ] Backend URL works: `https://your-app.railway.app/`
- [ ] API docs work: `https://your-app.railway.app/docs`
- [ ] Stats endpoint: `https://your-app.railway.app/api/stats`

### **Frontend (Vercel)**
- [ ] Frontend loads: `https://your-project.vercel.app`
- [ ] Dashboard shows stats
- [ ] Sources page shows sources from Supabase
- [ ] Can scrape content
- [ ] Can process content

---

## 🐛 **Troubleshooting**

### **Backend not starting on Railway**
1. Check logs in Railway dashboard
2. Verify all environment variables are set
3. Check Python version (should use 3.10+)

### **Frontend can't connect to backend**
1. Check `NEXT_PUBLIC_API_URL` is set correctly
2. Make sure Railway backend is running
3. Check browser console for CORS errors

### **CORS errors**
1. Update backend CORS to allow Vercel domain
2. Or keep `allow_origins=["*"]` for testing

---

## 📝 **Quick Commands Reference**

### **Deploy Backend**
```bash
# Railway does this automatically from GitHub
# Just push your code and Railway deploys
```

### **Deploy Frontend**
```bash
cd frontend
vercel --prod
```

### **Update Environment Variables**
```bash
# Backend (Railway): Use dashboard
# Frontend (Vercel):
vercel env add NEXT_PUBLIC_API_URL production
```

### **View Logs**
```bash
# Railway: Dashboard → Logs tab
# Vercel:
vercel logs
```

---

## 🎯 **Alternative: Deploy Both to Vercel**

If you want everything on Vercel:

### **Backend as Serverless Function**
1. Create `api/` folder in root
2. Move backend code to serverless functions
3. Deploy entire project to Vercel

**Note:** This requires restructuring. Railway is easier for FastAPI!

---

## 💰 **Costs**

### **Vercel**
- **Hobby (Free):** Perfect for your use case
- **Pro ($20/month):** If you need more

### **Railway**
- **Free tier:** $5 credit/month
- **Usage-based:** ~$5-10/month for this app

---

## 🎉 **Final Steps**

### **After Deployment:**

1. **Test Production URLs:**
   ```bash
   # Backend
   curl https://your-app.railway.app/api/stats
   
   # Frontend
   open https://your-project.vercel.app
   ```

2. **Update Documentation:**
   - Add production URLs to README
   - Share with team

3. **Monitor:**
   - Railway dashboard for backend logs
   - Vercel dashboard for frontend analytics

---

## 🚀 **You're Live!**

Your Content Automation system is now deployed and accessible worldwide!

**Frontend:** `https://your-project.vercel.app`  
**Backend:** `https://your-app.railway.app`  
**Database:** Supabase (already cloud-hosted)

---

## 📞 **Need Help?**

- Railway docs: https://docs.railway.app
- Vercel docs: https://vercel.com/docs
- Both have excellent support!

**Congratulations on your deployment!** 🎊
