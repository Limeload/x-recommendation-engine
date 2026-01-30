# Deploying Frontend to Vercel

This guide covers deploying the Next.js frontend to Vercel (fastest and easiest option).

## Prerequisites
- GitHub account with repository pushed
- Vercel account (free at [vercel.com](https://vercel.com))
- Backend deployed to Render (or another platform)

## Step 1: Deploy Frontend to Vercel

### Connect GitHub to Vercel

1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Click **"Import"**

### Configure Project

1. **Project Name**: `recommendation-engine-frontend`
2. **Framework Preset**: Next.js (should auto-detect)
3. **Root Directory**: Select `frontend`
4. **Environment Variables**: Add your backend URL
   ```
   NEXT_PUBLIC_API_URL=https://recommendation-engine-api.onrender.com
   ```
5. Click **"Deploy"**

Vercel will build and deploy automatically (2-3 minutes).

### Get Your URL
Once deployed, your frontend will be available at:
```
https://recommendation-engine-frontend.vercel.app
```

---

## Step 2: Update Backend CORS (if needed)

If you see CORS errors, update [backend/main.py](../backend/main.py):

```python
from fastapi.middleware.cors import CORSMiddleware

# Add your Vercel URL to allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://recommendation-engine-frontend.vercel.app",
        "localhost:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Step 3: Enable Auto-Deploy

Vercel auto-deploys when you push to `main`:
1. Make code changes in `frontend/` folder
2. Push to GitHub
3. Vercel automatically redeploys

---

## Troubleshooting

### Build fails
- Check **Deployments** → **"Logs"** tab
- Ensure `frontend/package.json` has correct scripts
- Verify Node version compatibility

### API calls fail / blank page
- Verify `NEXT_PUBLIC_API_URL` environment variable is set correctly
- Check browser console (F12) for errors
- Ensure backend is running and accessible

### Custom domain (optional)
1. Go to project settings → **"Domains"**
2. Add your custom domain
3. Update DNS records (instructions provided by Vercel)

---

## Benefits of Vercel for Next.js
✅ Free tier with generous limits
✅ Automatic deployments on git push
✅ Built-in Next.js optimization
✅ Edge functions support
✅ Environment variables management
✅ Preview deployments for PRs

## Cost
- **Free tier**: Unlimited deployments, 100GB bandwidth/month
- **Pro tier**: $20/month (optional, rarely needed)

Perfect for hosting your React frontend!
