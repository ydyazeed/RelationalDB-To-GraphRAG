# 🚀 Deployment Guide

Complete guide to deploy the RAG Knowledge Graph system with backend on Render and frontend on Vercel.

## 📋 Prerequisites

- GitHub account
- Render account (free tier): https://render.com
- Vercel account (free tier): https://vercel.com
- Gemini API Key: https://ai.google.dev/

## 🏗️ Architecture

```
Frontend (Vercel)  →  Backend API (Render)  →  Neo4j (Docker in Render)
     React              FastAPI + Neo4j           FAISS Vector Search
```

---

## 🖥️ Backend Deployment on Render

### Step 1: Push Code to GitHub

Your code is already in: https://github.com/ydyazeed/RelationalDB-To-GraphRAG.git

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Create Web Service

1. Click "New +" → "Web Service"
2. Connect to your GitHub repository: `RelationalDB-To-GraphRAG`
3. Configure:

   **Basic Info:**
   - Name: `rag-knowledge-graph`
   - Region: Choose closest to you
   - Branch: `main`

   **Build & Deploy:**
   - Environment: `Docker`
   - Docker Command: (leave empty, uses Dockerfile)

   **Instance Type:**
   - Free (512 MB RAM, sleeps after inactivity)
   - OR Starter ($7/month, always on, 512 MB RAM)

### Step 4: Environment Variables

Add these environment variables in Render dashboard:

```env
GEMINI_API_KEY=your_gemini_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
PORT=8000
```

### Step 5: Deploy

1. Click "Create Web Service"
2. Wait 5-10 minutes for initial build
3. Your API will be live at: `https://rag-knowledge-graph.onrender.com`

### Step 6: Test Backend

```bash
# Health check
curl https://rag-knowledge-graph.onrender.com/health

# Expected response:
{
  "api": "healthy",
  "neo4j": "connected",
  "vector_index": "not loaded",
  "graph_built": false
}
```

---

## 🎨 Frontend Deployment on Vercel

### Step 1: Update Frontend Environment

1. Edit `frontend/.env`:
```env
REACT_APP_API_URL=https://rag-knowledge-graph.onrender.com
```

2. Commit and push:
```bash
cd /Users/yazeedshamsudeen/Projects/SchemaExtractor
git add frontend/.env
git commit -m "Update API URL for production"
git push origin main
```

### Step 2: Deploy to Vercel

#### Option A: Via Vercel Dashboard (Recommended)

1. Go to https://vercel.com
2. Click "Add New..." → "Project"
3. Import your GitHub repository: `RelationalDB-To-GraphRAG`
4. Configure:

   **Framework Preset:** Create React App
   **Root Directory:** `frontend`
   **Build Command:** `npm run build`
   **Output Directory:** `build`

5. Environment Variables:
   ```env
   REACT_APP_API_URL=https://rag-knowledge-graph.onrender.com
   ```

6. Click "Deploy"

#### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy from frontend directory
cd frontend
vercel --prod
```

### Step 3: Your Frontend is Live!

Your app will be available at: `https://your-app.vercel.app`

---

## 🧪 Local Testing (Before Deployment)

### Test Backend Locally

```bash
# Terminal 1: Start backend
cd /Users/yazeedshamsudeen/Projects/SchemaExtractor
python3 rag_api_server.py
```

### Test Frontend Locally

```bash
# Terminal 2: Start frontend
cd /Users/yazeedshamsudeen/Projects/SchemaExtractor/frontend
npm start
```

### Test Complete Flow

1. Open http://localhost:3000
2. Go to "Build Graph" tab
3. Enter connection string: `postgresql://user:password@host:port/database`
4. Click "Build Graph"
5. Wait for completion (~60 seconds)
6. Go to "Chat" tab
7. Try query: "How many customers do we have?"

---

## 🐛 Troubleshooting

### Backend Issues

**Neo4j not starting:**
```bash
# Check Render logs
# Make sure memory settings are correct in Dockerfile
```

**API timeout:**
```bash
# Render free tier sleeps after inactivity
# First request may take 30-60 seconds to wake up
# Consider upgrading to Starter plan
```

**Build fails:**
```bash
# Check Render build logs
# Ensure all environment variables are set
# Verify Dockerfile syntax
```

### Frontend Issues

**CORS errors:**
```bash
# Backend already has CORS enabled
# Check that REACT_APP_API_URL is correct
# Ensure backend is running
```

**Build fails:**
```bash
# Check Node version (should be 18+)
# Clear cache: rm -rf node_modules package-lock.json && npm install
# Check for TypeScript errors
```

**API not connecting:**
```bash
# Verify environment variable in Vercel dashboard
# Check browser console for errors
# Test backend URL directly in browser
```

---

## 💰 Cost Breakdown

### Free Tier (Recommended for Testing)
- **Render Free**: $0/month
  - 512 MB RAM
  - Sleeps after 15 min inactivity
  - 750 hours/month
- **Vercel Free**: $0/month
  - Unlimited deployments
  - 100 GB bandwidth
  - Automatic HTTPS

**Total: $0/month**

### Production Tier
- **Render Starter**: $7/month
  - 512 MB RAM
  - Always on
  - No sleep
- **Vercel Pro**: $20/month (optional)
  - More bandwidth
  - Analytics

**Total: $7-27/month**

---

## 📝 Post-Deployment Checklist

- [ ] Backend API is accessible
- [ ] Neo4j is running in backend
- [ ] Frontend can reach backend API
- [ ] Build Graph feature works
- [ ] Chat feature works
- [ ] Environment variables are set correctly
- [ ] HTTPS is working on both services
- [ ] Monitor Render logs for errors

---

## 🔄 Updating Your Deployment

### Update Backend

```bash
# Make changes to backend code
git add .
git commit -m "Update backend"
git push origin main

# Render auto-deploys on push
# Or manually deploy in Render dashboard
```

### Update Frontend

```bash
# Make changes to frontend code
cd frontend
git add .
git commit -m "Update frontend"
git push origin main

# Vercel auto-deploys on push
# Or redeploy in Vercel dashboard
```

---

## 🎯 Quick Deploy Commands

```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Deploy backend on Render (via dashboard)
# 3. Deploy frontend on Vercel (via dashboard or CLI)

# OR use Vercel CLI
cd frontend
vercel --prod
```

---

## 🆘 Support

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **GitHub Issues**: https://github.com/ydyazeed/RelationalDB-To-GraphRAG/issues

---

## ✅ Success!

Your RAG Knowledge Graph system is now live!

- 🌐 **Frontend**: `https://your-app.vercel.app`
- 🔧 **Backend API**: `https://rag-knowledge-graph.onrender.com`

Share your deployed app with others! 🎉

