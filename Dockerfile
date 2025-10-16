# Multi-stage Docker build for Render deployment
FROM neo4j:5.15-community as neo4j-base

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    openjdk-17-jre \
    && rm -rf /var/lib/apt/lists/*

# Copy Neo4j from base image
COPY --from=neo4j-base /var/lib/neo4j /var/lib/neo4j
COPY --from=neo4j-base /startup /startup

# Set Neo4j environment variables
ENV NEO4J_HOME=/var/lib/neo4j \
    NEO4J_AUTH=neo4j/password \
    NEO4J_dbms_memory_pagecache_size=512M \
    NEO4J_dbms_memory_heap_initial__size=512M \
    NEO4J_dbms_memory_heap_max__size=1G

# Set working directory
WORKDIR /app

# Copy Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Neo4j in background\n\
/startup/docker-entrypoint.sh neo4j &\n\
echo "Waiting for Neo4j to start..."\n\
sleep 15\n\
\n\
# Check if Neo4j is ready\n\
until curl -s http://localhost:7474 > /dev/null; do\n\
  echo "Waiting for Neo4j..."\n\
  sleep 2\n\
done\n\
echo "Neo4j is ready!"\n\
\n\
# Start FastAPI\n\
exec python3 rag_api_server.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE 8000 7474 7687

# Start services
CMD ["/app/start.sh"]

