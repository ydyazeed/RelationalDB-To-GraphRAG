# 🤖 RAG Knowledge Graph System

AI-powered Retrieval-Augmented Generation (RAG) system that converts PostgreSQL databases into queryable knowledge graphs with semantic search.

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

### 4. Start the RAG Server
```bash
python3 rag_api_server.py
```

Server will start at: `http://localhost:8000`

### 5. Build Knowledge Graph

Send your PostgreSQL connection string to build the graph:

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
  "next_steps": [
    "1. Monitor progress at GET /health endpoint",
    "2. Once graph_built=true, use POST /chat endpoint to query",
    "3. Example: POST /chat with {\"query\": \"How many customers?\", \"stream\": false}"
  ],
  "estimated_time": "30-60 seconds for small databases"
}
```

### 6. Query with AI Agent

Once the graph is built, start querying:

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

## 📡 API Endpoints

### Check System Health
```bash
curl http://localhost:8000/health
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

## 🎯 Example Queries

### Simple Queries
```bash
# Count records
"How many customers do we have?"
"How many products are there?"

# Get statistics
"Show me the graph statistics"
```

### Semantic Search (FAISS)
```bash
# Find similar items
"Find products related to wireless audio"
"Show me electronic products"
"Products similar to smartphones"
```

### Entity Lookup
```bash
# Get details
"Tell me about customer Aisha Khan"
"Give me details about Ravi Patel"
```

### Relationship Queries (Graph Traversal)
```bash
# Navigate relationships
"What products has Aisha Khan ordered?"
"Which customers bought Smartphone Model X?"
"What products are in the Electronics category?"
```

### Complex Queries
```bash
# Multi-hop queries
"Which customers have bought products from the Electronics category?"
"Show me customers who have placed more than one order"
"What is the total value of all orders?"
```

## 🧠 How It Works

1. **Schema Extraction** - Extracts database schema, detects relationships
2. **Ontology Generation** - Gemini LLM creates intelligent graph structure
3. **Knowledge Graph** - Builds Neo4j graph with nodes and relationships
4. **Vector Indexing** - Creates FAISS embeddings for semantic search
5. **AI Agent** - LangGraph agent with dynamic tool selection:
   - `vector_search` - Semantic similarity (FAISS)
   - `cypher_query` - Graph traversal (Neo4j)
   - `get_node_details` - Entity lookup
   - `filter_nodes` - Property filtering
   - `graph_stats` - Statistics

## 🛠️ Technologies

- **Database**: PostgreSQL, Neo4j
- **Vector Search**: FAISS, Sentence Transformers
- **AI/LLM**: Google Gemini 2.5 Flash
- **Agent**: LangGraph, LangChain
- **API**: FastAPI
- **Language**: Python 3.13+

## 📁 Project Files

```
SchemaExtractor/
├── .env                        # Environment variables
├── requirements.txt            # Dependencies
├── rag_api_server.py          # Main API server
├── schema_extractor.py        # PostgreSQL extraction
├── schema_to_ontology.py      # Ontology generation
├── create_knowledge_graph.py  # Neo4j builder
├── vector_indexer.py          # FAISS indexing
└── demo_rag_system.py         # Demo script
```

## 🧪 Testing

Run the comprehensive demo:
```bash
python3 demo_rag_system.py
```

## 🐛 Troubleshooting

**Server not starting?**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
pkill -f rag_api_server

# Restart
python3 rag_api_server.py
```

**Neo4j not running?**
```bash
# Check Neo4j
docker ps | grep neo4j

# Start Neo4j
docker start neo4j
```

**Graph not built?**
```bash
# Check health
curl http://localhost:8000/health

# Look for graph_built: true
```

## 📝 Environment Variables Reference

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Neo4j (Required)
NEO4J_URI=bolt://localhost:7687          # Or neo4j+s://xxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

## 🎉 That's It!

You now have a complete RAG system that can:
- ✅ Extract schemas from any PostgreSQL database
- ✅ Build knowledge graphs automatically
- ✅ Perform semantic search with FAISS
- ✅ Answer complex questions using AI
- ✅ Navigate graph relationships intelligently

---

**Need help?** Open an issue or check the server logs at `server.log`
