# Deploying to Render

This guide covers deploying both the FastAPI backend and Next.js frontend to Render.

## Prerequisites
- GitHub account with your repository pushed
- Render account (free at [render.com](https://render.com))

## Step 1: Deploy Backend to Render

### Create Backend Web Service

1. Go to [render.com/dashboard](https://render.com/dashboard)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `recommendation-engine-api`
   - **Region**: Choose closest to users (e.g., Oregon for US)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3.11`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Environment Variables** (add these):
   ```
   DEBUG=false
   USE_VECTOR_DB=false
   PYTHONUNBUFFERED=1
   ```

6. Click **"Create Web Service"** and wait for deployment (3-5 min)

7. Note your backend URL: `https://recommendation-engine-api.onrender.com`

### Verify Backend
Once deployed, test it:
```bash
curl https://recommendation-engine-api.onrender.com/health
```

---

## Step 2: Deploy Frontend to Render

### Create Frontend Web Service

1. Go to [render.com/dashboard](https://render.com/dashboard)
2. Click **"New +"** → **"Web Service"**
3. Connect the same GitHub repository
4. Configure:
   - **Name**: `recommendation-engine-ui`
   - **Region**: Same as backend
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Runtime**: `Node`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run start`

5. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://recommendation-engine-api.onrender.com
   NODE_ENV=production
   ```

6. Click **"Create Web Service"** and wait for deployment

7. Your frontend URL: `https://recommendation-engine-ui.onrender.com`

---

## Step 3: Enable Auto-Deploy

Both services should now auto-deploy when you push to `main` branch.

To verify:
1. Make a small code change
2. Push to GitHub
3. Check Render dashboard for automatic deployment

---

## Troubleshooting

### Backend not starting
- Check **Logs** tab in Render dashboard
- Verify Python dependencies: `pip install -r requirements.txt` works locally
- Ensure `main.py` exists and FastAPI app is correctly initialized

### Frontend shows blank page
- Check **Environment Variables** → `NEXT_PUBLIC_API_URL` is set correctly
- Verify backend is running and accessible
- Check browser console (F12) for errors

### CORS errors
The backend's CORS configuration should allow frontend URL. Verify in [backend/main.py](../backend/main.py):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your Render frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Connection timeout
- Free tier instances sleep after 15 min of inactivity
- Upgrade to paid plan ($7/month) for always-on services
- Or use a ping service to keep it awake

---

## Monitoring & Logs

1. **Backend Logs**: Go to service → **"Logs"** tab
2. **Frontend Logs**: Go to service → **"Logs"** tab
3. **Metrics**: Monitor CPU, memory usage in service details

---

## Next Steps

- Set up a database (PostgreSQL add-on available on Render)
- Configure custom domain
- Set up error tracking (Sentry, etc.)

## Cost
- **Free tier**: 0.5 CPU, 512MB RAM per service
- **Pro tier**: $7/month per service for always-on

Your current setup should run fine on free tier for development/testing.
