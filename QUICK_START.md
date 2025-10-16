# ⚡ Quick Start Commands

## 1️⃣ Setup (One Time)

```bash
# Clone repo
git clone https://github.com/ydyazeed/RelationalDB-To-GraphRAG.git
cd RelationalDB-To-GraphRAG

# Install dependencies
pip3 install -r requirements.txt

# Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
EOF

# Start Neo4j (Docker)
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

## 2️⃣ Start Server

```bash
python3 rag_api_server.py
```

## 3️⃣ Build Graph

```bash
curl -X POST http://localhost:8000/build-graph \
  -H "Content-Type: application/json" \
  -d '{
    "connection_string": "postgresql://user:password@host:port/database"
  }'
```

## 4️⃣ Query

```bash
# Simple query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How many customers?", "stream": false}'

# Semantic search
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Find wireless products", "stream": false}'

# Relationship query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What did Aisha Khan order?", "stream": false}'
```

## 🔍 Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Run demo
python3 demo_rag_system.py
```

That's it! 🚀

