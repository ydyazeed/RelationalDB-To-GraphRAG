# 🤖 RAG Knowledge Graph System

AI-powered Retrieval-Augmented Generation (RAG) system that converts PostgreSQL databases into queryable knowledge graphs with semantic search.

---

## 🎥 Demo Videos

### 📺 Video 1: Building Knowledge Graph from PostgreSQL
[![Watch Demo 1](https://img.youtube.com/vi/zWcS3tH2NoQ/maxresdefault.jpg)](https://youtu.be/zWcS3tH2NoQ)

**[▶️ Watch on YouTube](https://youtu.be/zWcS3tH2NoQ)**

---

### 📺 Video 2: AI Chat Agent Query Interface
[![Watch Demo 2](https://img.youtube.com/vi/leuOQQ23V6Q/maxresdefault.jpg)](https://youtu.be/leuOQQ23V6Q)

**[▶️ Watch on YouTube](https://youtu.be/leuOQQ23V6Q)**

---

## 🏗️ System Architecture

![Architectural Diagram](Architectural-diagram.png)

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/ydyazeed/RelationalDB-To-GraphRAG.git
cd RelationalDB-To-GraphRAG
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# Required: Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Required: Neo4j Database (local or cloud)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

**Get Gemini API Key**: https://ai.google.dev/

**Start Local Neo4j** (using Docker):
```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### 4. Start the Backend API Server
```bash
python3 rag_api_server.py
```

Server will start at: `http://localhost:8000`

### 5. Start the Frontend (Optional)
```bash
cd frontend
npm install
npm start
```

Frontend will open at: `http://localhost:3000`

### 6. Build Knowledge Graph

**Using Frontend:**
- Go to "Build Graph" tab
- Paste your PostgreSQL connection string
- Click "Build Graph"
- Wait for completion

**Using API:**
```bash
curl -X POST http://localhost:8000/build-graph \
  -H "Content-Type: application/json" \
  -d '{
    "connection_string": "postgresql://user:password@host:port/database"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Knowledge graph build started in background",
  "estimated_time": "30-60 seconds for small databases"
}
```

### 7. Query with AI Agent

**Using Frontend:**
- Go to "Chat" tab
- Type your query
- Get AI-powered responses with reasoning

**Using API:**
```bash
# Simple query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How many customers do we have?", "stream": false}'

# Semantic search
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Find products related to wireless audio", "stream": false}'

# Relationship query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What products has customer Aisha Khan ordered?", "stream": false}'
```

---

## 📡 API Endpoints

### Check System Health
```bash
GET /health
```

### Build Knowledge Graph
```bash
POST /build-graph
Body: {"connection_string": "postgresql://..."}
```

### Chat with AI Agent
```bash
POST /chat
Body: {"query": "your question here", "stream": false}
```

**Response Format:**
```json
{
  "response": "AI-generated answer",
  "reasoning": ["Step 1: Using tool...", "Step 2: ..."],
  "tools_used": ["vector_search", "cypher_query"],
  "sources": [
    {
      "tool": "vector_search",
      "content": "Found 5 similar entities..."
    }
  ]
}
```

---

## 🎯 Example Queries

### Simple Queries
- "How many customers do we have?"
- "How many products are there?"
- "Show me the graph statistics"

### Semantic Search (FAISS)
- "Find products related to wireless audio"
- "Show me electronic products"
- "Products similar to smartphones"

### Entity Lookup
- "Tell me about customer Aisha Khan"
- "Give me details about Ravi Patel"

### Relationship Queries (Graph Traversal)
- "What products has Aisha Khan ordered?"
- "Which customers bought Smartphone Model X?"
- "What products are in the Electronics category?"

### Complex Queries
- "Which customers have bought products from the Electronics category?"
- "Show me customers who have placed more than one order"
- "What is the total value of all orders?"

---

## 🧠 How It Works

1. **Schema Extraction** - Extracts database schema, detects relationships (explicit & implicit)
2. **Ontology Generation** - Gemini LLM creates intelligent graph structure
3. **Knowledge Graph** - Builds Neo4j graph with nodes and relationships
4. **Vector Indexing** - Creates FAISS embeddings for semantic search
5. **AI Agent** - LangGraph agent with dynamic tool selection:
   - `vector_search` - Semantic similarity (FAISS)
   - `cypher_query` - Graph traversal (Neo4j)
   - `get_node_details` - Entity lookup
   - `filter_nodes` - Property filtering
   - `graph_stats` - Statistics

---

## 🛠️ Tech Stack

### Backend
- **Database**: PostgreSQL, Neo4j
- **Vector Search**: FAISS, Sentence Transformers
- **AI/LLM**: Google Gemini 2.5 Flash
- **Agent**: LangGraph, LangChain
- **API**: FastAPI, Uvicorn
- **Language**: Python 3.11+

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Custom CSS (Red & Black Theme)
- **HTTP Client**: Axios
- **Markdown**: react-markdown

---

## 📁 Project Structure

```
SchemaExtractor/
├── backend/
│   ├── rag_api_server.py          # Main API server
│   ├── schema_extractor.py        # PostgreSQL extraction
│   ├── schema_to_ontology.py      # Ontology generation
│   ├── create_knowledge_graph.py  # Neo4j builder
│   ├── vector_indexer.py          # FAISS indexing
│   └── requirements.txt           # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BuildGraph.tsx     # Graph building UI
│   │   │   └── Chat.tsx           # Chat interface
│   │   └── App.tsx                # Main app
│   └── package.json               # Node dependencies
│
├── Dockerfile                     # Docker configuration
├── docker-compose.yml             # Multi-container setup
└── .env                          # Environment variables
```

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Start all services (Neo4j + Backend)
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build
```bash
# Build image
docker build -t rag-kg-system .

# Run container
docker run -d -p 8000:8000 -p 7474:7474 -p 7687:7687 \
  -e GEMINI_API_KEY=your_key \
  rag-kg-system
```

---

## ☁️ Cloud Deployment

### Deploy Backend to Render
1. Fork/Push this repo to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Create new **Web Service**
4. Connect your GitHub repo
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `python rag_api_server.py`
7. Add environment variables:
   - `GEMINI_API_KEY`
   - `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
8. Deploy!

### Deploy Frontend to Vercel
1. Go to [Vercel Dashboard](https://vercel.com)
2. Import your GitHub repo
3. Set root directory to `frontend`
4. Add environment variable: `REACT_APP_API_URL=your-render-url`
5. Deploy!

---

## 🧪 Testing

Run the comprehensive demo:
```bash
python3 demo_rag_system.py
```

Test individual components:
```bash
# Test schema extraction
python3 schema_extractor.py

# Test ontology generation
python3 schema_to_ontology.py

# Test knowledge graph creation
python3 create_knowledge_graph.py

# Test vector indexing
python3 vector_indexer.py
```

---

## 🐛 Troubleshooting

### Server not starting?
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
pkill -f rag_api_server

# Restart
python3 rag_api_server.py
```

### Neo4j not running?
```bash
# Check Neo4j
docker ps | grep neo4j

# Start Neo4j
docker start neo4j

# View logs
docker logs neo4j
```

### Graph not built?
```bash
# Check health
curl http://localhost:8000/health

# Look for graph_built: true
```

### Frontend not connecting?
```bash
# Check .env file
cat frontend/.env

# Should have: REACT_APP_API_URL=http://localhost:8000

# Restart frontend
cd frontend && npm start
```

---

## 📝 Environment Variables

```env
# Backend (.env in root)
GEMINI_API_KEY=your_gemini_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Frontend (frontend/.env)
REACT_APP_API_URL=http://localhost:8000
```

---

## 🎉 Features

- ✅ **Automatic Schema Extraction** - Extracts tables, columns, relationships from PostgreSQL
- ✅ **Implicit Relationship Detection** - Finds hidden connections not defined by foreign keys
- ✅ **AI-Powered Ontology** - Gemini LLM creates intelligent graph structure
- ✅ **Knowledge Graph** - Neo4j graph database with bulk CSV import
- ✅ **Semantic Search** - FAISS vector indexing for similarity search
- ✅ **Intelligent AI Agent** - LangGraph agent with dynamic tool selection
- ✅ **Modern UI** - React frontend with dark red-black theme
- ✅ **Streaming Responses** - Real-time AI responses with reasoning chain
- ✅ **Production Ready** - Docker, Docker Compose, Cloud deployment support
- ✅ **RESTful API** - FastAPI with CORS support

---

## 📊 Performance

- **Schema Extraction**: ~5-10 seconds for 10 tables
- **Ontology Generation**: ~10-20 seconds (Gemini LLM)
- **Graph Building**: ~10-30 seconds for 1000 nodes
- **Vector Indexing**: ~5-15 seconds for 1000 nodes
- **Query Response**: ~1-3 seconds (with tool calls)

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

---

## 🙏 Acknowledgments

- **Google Gemini** - AI/LLM capabilities
- **Neo4j** - Graph database
- **LangChain/LangGraph** - Agent orchestration
- **FAISS** - Vector similarity search
- **FastAPI** - High-performance API framework
- **React** - Modern frontend framework

---

## 📧 Contact

For questions or support, open an issue on GitHub.

---

**Built with ❤️ by Yazeed**
