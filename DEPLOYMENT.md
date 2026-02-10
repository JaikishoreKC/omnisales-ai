# Deployment Guide

## Backend Deployment (Render)

### Prerequisites
- Render account
- MongoDB Atlas cluster
- OpenRouter API key

### Steps

1. **Push code to GitHub**
```bash
cd backend
git init
git add .
git commit -m "Initial backend commit"
git push origin main
```

2. **Create Web Service on Render**
- Go to https://render.com
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Use `render.yaml` settings or configure manually:
  - **Runtime**: Python 3
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - **Root Directory**: `backend`

3. **Set Environment Variables**
```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=omnisales
OPENROUTER_API_KEY=your_api_key
SECRET_KEY=generate_with_openssl_rand_hex_32
FRONTEND_URL=https://your-frontend.vercel.app
ENVIRONMENT=production
```

4. **Deploy**
- Click "Create Web Service"
- Wait for deployment to complete

---

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account
- Backend deployed and URL available

### Steps

1. **Push code to GitHub**
```bash
cd frontend
git init
git add .
git commit -m "Initial frontend commit"
git push origin main
```

2. **Import Project to Vercel**
- Go to https://vercel.com
- Click "New Project"
- Import your GitHub repository
- Select `frontend` directory as root

3. **Configure Build Settings**
- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

4. **Set Environment Variables**
```
VITE_API_BASE_URL=https://your-backend.onrender.com
```

5. **Deploy**
- Click "Deploy"
- Wait for deployment to complete

---

## Post-Deployment

### Update CORS Settings
Update backend `FRONTEND_URL` environment variable with your Vercel URL.

### Test Endpoints
```bash
# Health check
curl https://your-backend.onrender.com/health

# Chat endpoint
curl -X POST https://your-backend.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "session_id": "test_session",
    "message": "Hello",
    "channel": "web"
  }'
```

### Load Sample Data
```bash
# SSH into Render or run locally
python load_products.py
```

---

## Monitoring

### Render
- View logs: Dashboard → Your Service → Logs
- Monitor metrics: CPU, Memory, Request count

### Vercel
- View deployments: Dashboard → Your Project → Deployments
- Check analytics: Dashboard → Analytics

---

## Troubleshooting

### Backend Issues
- Check Render logs for errors
- Verify all environment variables are set
- Test MongoDB connection
- Verify OpenRouter API key is valid

### Frontend Issues
- Check browser console for errors
- Verify VITE_API_BASE_URL is correct
- Check Network tab for failed requests
- Verify CORS settings on backend
