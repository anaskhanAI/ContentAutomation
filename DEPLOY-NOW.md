# ⚡ Deploy in 10 Minutes - Quick Guide

## 🎯 **Fastest Deployment Path**

### **Step 1: Deploy Backend (5 min)**

```bash
# 1. Go to https://railway.app
# 2. Click "New Project" → "Deploy from GitHub"
# 3. Select your repo
# 4. Railway auto-detects and deploys
# 5. Go to Settings:
#    - Root Directory: backend
#    - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
# 6. Go to Variables → Add all env vars from your .env file
# 7. Copy the generated URL (e.g., https://xyz.up.railway.app)
```

---

### **Step 2: Deploy Frontend (5 min)**

```bash
# In your terminal:
cd frontend

# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Add backend URL
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://xyz.up.railway.app (from Step 1)

# Deploy to production
vercel --prod
```

---

## ✅ **Done!**

Your app is live at: `https://your-project.vercel.app`

---

## 🔑 **Environment Variables Needed**

### **Railway (Backend)**
Copy these from your `.env` file:
```
OPUS_API_KEY
OPUS_WORKFLOW_ID
FIRECRAWL_API_KEY
SUPABASE_URL
SUPABASE_KEY
```

### **Vercel (Frontend)**
Only one needed:
```
NEXT_PUBLIC_API_URL=https://your-railway-url.railway.app
```

---

## 🧪 **Test Deployment**

```bash
# Test backend
curl https://your-railway-url.railway.app/api/stats

# Test frontend
open https://your-vercel-url.vercel.app
```

---

## 💡 **Pro Tips**

1. **Vercel auto-deploys** on git push to main
2. **Railway auto-deploys** on git push to main
3. Both have free tiers perfect for this app
4. Check logs in dashboards if issues

---

**That's it! You're deployed!** 🚀

Full guide: `VERCEL-DEPLOYMENT-GUIDE.md`
