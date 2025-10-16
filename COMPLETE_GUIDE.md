# 🎯 Complete Guide - RAG Knowledge Graph System

## 📁 Project Structure

```
RelationalDB-To-GraphRAG/
├── backend/
│   ├── rag_api_server.py          # Main FastAPI server
│   ├── schema_extractor.py         # PostgreSQL extraction
│   ├── schema_to_ontology.py       # Gemini ontology generation
│   ├── create_knowledge_graph.py   # Neo4j graph builder
│   ├── vector_indexer.py           # FAISS vector indexing
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Docker config for Render
│   └── .env                        # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Main app with tabs
│   │   ├── App.css                # Dark theme styles
│   │   └── components/
│   │       ├── BuildGraph.tsx     # Build graph interface
│   │       ├── BuildGraph.css
│   │       ├── Chat.tsx           # Chat interface
│   │       └── Chat.css
│   ├── package.json
│   └── .env                       # API URL config
│
├── README.md                       # Quick start guide
├── DEPLOYMENT.md                   # Deployment instructions
└── test-local.sh                  # Local testing script
```

---

## 🚀 Quick Start (Local)

### 1. Backend Setup

```bash
# Install dependencies
pip3 install -r requirements.txt

# Set up environment
cat > .env << EOF
GEMINI_API_KEY=your_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
EOF

# Start Neo4j
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Start backend
python3 rag_api_server.py
```

### 2. Frontend Setup

```bash
# Go to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start frontend
npm start
```

### 3. Test Everything

```bash
# Run test script
./test-local.sh

# Open browser
open http://localhost:3000
```

---

## 🌐 Deployment

### Backend on Render

1. **Create Web Service**:
   - Go to https://render.com
   - New → Web Service
   - Connect GitHub repo
   - Environment: Docker
   - Add env vars: `GEMINI_API_KEY`, etc.

2. **Deploy**: 
   - Click "Create Web Service"
   - Wait 5-10 minutes
   - API live at: `https://your-app.onrender.com`

### Frontend on Vercel

1. **Update Environment**:
   ```bash
   cd frontend
   echo "REACT_APP_API_URL=https://your-app.onrender.com" > .env
   ```

2. **Deploy**:
   ```bash
   npm i -g vercel
   vercel --prod
   ```
   OR use Vercel Dashboard

3. **Live**: `https://your-app.vercel.app`

Full details in [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 🎨 Frontend Features

### Build Graph Tab
- **Connection String Input**: Enter PostgreSQL connection
- **Build Button**: Start graph build process
- **Live Progress**: Real-time status updates
- **Success Message**: Confirmation when ready

### Chat Tab
- **Query Input**: Ask questions in natural language
- **AI Responses**: Formatted with markdown
- **Tool Tracking**: See which tools AI used
- **Reasoning Chain**: View AI's thought process
- **Sources**: See data sources used
- **Example Queries**: Quick-start suggestions

### UI Features
- 🌑 Dark theme
- ⚡ Real-time updates
- 📱 Responsive design
- 🎨 Modern animations
- 💬 Message history
- 🔍 Expandable details

---

## 🔧 API Endpoints

### Backend API

```bash
GET  /                  # API info
GET  /health            # System status
POST /build-graph       # Build knowledge graph
POST /chat              # Query AI agent
GET  /stats             # Graph statistics
```

### Example Requests

**Build Graph:**
```bash
curl -X POST http://localhost:8000/build-graph \
  -H "Content-Type: application/json" \
  -d '{
    "connection_string": "postgresql://user:pass@host:port/db"
  }'
```

**Chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many customers do we have?",
    "stream": false
  }'
```

---

## 🧪 Testing Checklist

### Local Testing
- [ ] Neo4j running on port 7687
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can access frontend UI
- [ ] Build Graph tab loads
- [ ] Can enter connection string
- [ ] Graph builds successfully
- [ ] Chat tab loads
- [ ] Can send queries
- [ ] Receives AI responses
- [ ] Tools tracking works
- [ ] Reasoning chain visible

### Deployment Testing
- [ ] Backend deployed on Render
- [ ] Backend health endpoint responds
- [ ] Frontend deployed on Vercel
- [ ] Frontend can reach backend
- [ ] CORS working correctly
- [ ] Build graph works in production
- [ ] Chat works in production
- [ ] HTTPS working

---

## 💡 Example Queries

### Simple Queries
```
How many customers do we have?
How many products are there?
Show me the graph statistics
```

### Semantic Search
```
Find products related to wireless audio
Show me electronic products
Products similar to smartphones
```

### Relationship Queries
```
What products has customer Aisha Khan ordered?
Which customers bought Smartphone Model X?
What products are in the Electronics category?
```

### Complex Queries
```
Which customers have bought products from the Electronics category?
Show me customers who have placed more than one order
What is the total value of all orders?
```

---

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Web framework
- **Neo4j**: Graph database
- **FAISS**: Vector search
- **Gemini LLM**: AI model
- **LangGraph**: Agent framework
- **Sentence Transformers**: Embeddings

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Axios**: API client
- **React Markdown**: Response formatting
- **CSS3**: Modern styling

### Deployment
- **Render**: Backend hosting
- **Vercel**: Frontend hosting
- **Docker**: Containerization
- **GitHub**: Version control

---

## 📊 System Flow

```
1. User enters PostgreSQL connection string
        ↓
2. Backend extracts schema
        ↓
3. Gemini LLM generates ontology
        ↓
4. Neo4j graph created
        ↓
5. FAISS vector index built
        ↓
6. User queries via chat
        ↓
7. AI agent selects tools:
   - vector_search (semantic)
   - cypher_query (graph)
   - filter_nodes (exact)
        ↓
8. Results displayed with reasoning
```

---

## 🐛 Troubleshooting

### "Backend not responding"
```bash
# Check if backend is running
curl http://localhost:8000/health

# Restart backend
python3 rag_api_server.py
```

### "Neo4j connection failed"
```bash
# Check Neo4j
docker ps | grep neo4j

# Restart Neo4j
docker restart neo4j
```

### "CORS error"
```bash
# Backend CORS is already configured
# Check frontend .env has correct API URL
cat frontend/.env
```

### "Graph not building"
```bash
# Check logs
tail -f server.log

# Verify connection string format
postgresql://user:password@host:port/database
```

---

## 📚 Documentation

- [README.md](./README.md) - Quick start
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment guide
- [frontend/README.md](./frontend/README.md) - Frontend docs
- [QUICK_START.md](./QUICK_START.md) - Quick commands

---

## 🎉 Success!

Your RAG Knowledge Graph system is ready!

- ✅ PostgreSQL → Knowledge Graph conversion
- ✅ AI-powered querying with Gemini LLM
- ✅ Semantic search with FAISS
- ✅ Modern dark-themed UI
- ✅ Real-time status updates
- ✅ Production-ready deployment

**Repository**: https://github.com/ydyazeed/RelationalDB-To-GraphRAG

Happy coding! 🚀

