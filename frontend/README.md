# RAG Knowledge Graph Frontend

Modern dark-themed React interface for the RAG Knowledge Graph system.

## Features

- 🏗️ **Build Graph Tab**: Convert PostgreSQL databases to knowledge graphs
- 💬 **Chat Tab**: Query your knowledge graph with AI
- 🎨 **Dark Theme**: Modern, clean UI
- 📊 **Real-time Status**: Live updates during graph building
- 🔍 **Source Tracking**: See which tools the AI used

## Local Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Environment Variables

Create a `.env` file:

```env
REACT_APP_API_URL=http://localhost:8000
```

For production:

```env
REACT_APP_API_URL=https://your-backend.onrender.com
```

## Deployment

Deploy to Vercel:

```bash
npm i -g vercel
vercel --prod
```

Or use Vercel Dashboard with these settings:
- Framework: Create React App
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `build`

## Tech Stack

- React 18 with TypeScript
- Axios for API calls
- React Markdown for formatted responses
- CSS3 with modern animations
