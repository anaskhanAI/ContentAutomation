# FastAPI Backend

REST API for Content Automation System

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`

API Documentation (Swagger): `http://localhost:8000/docs`

---

## 📡 API Endpoints

### **Dashboard & Stats**
- `GET /` - Health check
- `GET /api/stats` - Dashboard statistics

### **Scraping**
- `POST /api/scrape` - Trigger content scraping
- `GET /api/scrape/status/{task_id}` - Get scraping task status

### **Processing**
- `POST /api/process` - Trigger Opus job submission
- `GET /api/process/status/{task_id}` - Get processing task status

### **Content Sources**
- `GET /api/sources` - List all sources
- `POST /api/sources` - Create new source
- `PATCH /api/sources/{id}` - Update source
- `PATCH /api/sources/{id}/toggle` - Toggle active status
- `DELETE /api/sources/{id}` - Delete source (soft delete)

### **Settings**
- `GET /api/settings` - Get current settings
- `PATCH /api/settings` - Update settings

### **Activity**
- `GET /api/activity` - Get recent Opus jobs

---

## 🚢 Deployment

### Railway.app

1. Create account at railway.app
2. New Project → Deploy from GitHub
3. Select your repository
4. **Settings:**
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables:** Copy from main `.env` file
6. Deploy!

### Render.com

1. Create account at render.com
2. New Web Service
3. Connect GitHub repository
4. **Settings:**
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port 8000`
5. **Environment Variables:** Add all from `.env`
6. Create Service!

---

## 🔐 Environment Variables

Required (copy from main `.env` file):
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `FIRECRAWL_API_KEY`
- `OPUS_API_KEY`
- `OPUS_WORKFLOW_ID`
- All other settings from main `.env`

---

## 📝 Notes

- CORS is enabled for all origins (update for production)
- Task status stored in-memory (use Redis for production)
- Settings updates are session-only (persist to .env for permanent)
