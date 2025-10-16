"""
RAG API Server with Knowledge Graph and AI Agent
Combines Neo4j, FAISS vector search, and LangGraph agent
"""

import os
import sys
import subprocess
import json
from typing import Optional, List, Dict, Any, AsyncGenerator
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from neo4j import GraphDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from vector_indexer import VectorIndexer

load_dotenv()

app = FastAPI(
    title="Knowledge Graph RAG API",
    description="AI-powered knowledge graph with vector search and intelligent querying",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
graph_built = True  # Set to True since graph already exists
vector_indexer = None
neo4j_driver = None

# Request/Response models
class BuildGraphRequest(BaseModel):
    connection_string: str
    rebuild: bool = False

class ChatRequest(BaseModel):
    query: str
    stream: bool = True

class ChatResponse(BaseModel):
    response: str
    reasoning: List[str]
    tools_used: List[str]
    sources: List[Dict[str, Any]]

# Initialize connections
def get_neo4j_driver():
    global neo4j_driver
    if not neo4j_driver:
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        neo4j_driver = GraphDatabase.driver(uri, auth=(user, password))
    return neo4j_driver

def get_vector_indexer():
    global vector_indexer
    if not vector_indexer:
        vector_indexer = VectorIndexer()
        try:
            vector_indexer.load_index()
        except:
            pass
    return vector_indexer

# Tool functions for the AI agent
def vector_search_tool(query: str, k: int = 5) -> str:
    """
    Semantic search across all nodes using FAISS vector similarity.
    Use this for finding entities by meaning, not exact keywords.
    """
    try:
        indexer = get_vector_indexer()
        results = indexer.search(query, k=k)
        
        output = f"Found {len(results)} similar entities:\n"
        for r in results:
            output += f"- {r['type']}: {r['text']} (score: {r['similarity_score']:.3f})\n"
        
        return output
    except Exception as e:
        return f"Vector search error: {str(e)}"

def cypher_query_tool(cypher: str) -> str:
    """
    Execute a Cypher query on the Neo4j knowledge graph.
    Use for complex graph traversals and pattern matching.
    IMPORTANT: Always use LIMIT to avoid large result sets.
    """
    try:
        driver = get_neo4j_driver()
        
        # Add safety limit if not present
        if "LIMIT" not in cypher.upper():
            cypher += " LIMIT 10"
        
        with driver.session() as session:
            result = session.run(cypher)
            records = [dict(record) for record in result]
            
            if not records:
                return "No results found"
            
            return json.dumps(records, indent=2, default=str)
    
    except Exception as e:
        return f"Cypher query error: {str(e)}"

def get_node_details_tool(node_type: str, node_id: str) -> str:
    """
    Get detailed information about a specific node.
    Use when you have an exact node ID from vector search or other queries.
    """
    try:
        driver = get_neo4j_driver()
        
        with driver.session() as session:
            query = f"""
            MATCH (n:{node_type} {{nodeId: $node_id}})
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN n, collect({{
                relationship: type(r),
                target: labels(m)[0],
                target_id: m.nodeId
            }}) as relationships
            """
            result = session.run(query, node_id=node_id)
            record = result.single()
            
            if not record:
                return f"Node {node_type}:{node_id} not found"
            
            node_props = dict(record["n"])
            relationships = record["relationships"]
            
            output = f"Node: {node_type} (ID: {node_id})\n"
            output += f"Properties: {json.dumps(node_props, indent=2, default=str)}\n"
            output += f"Relationships: {json.dumps(relationships, indent=2)}\n"
            
            return output
    
    except Exception as e:
        return f"Error getting node details: {str(e)}"

def graph_stats_tool() -> str:
    """
    Get statistics about the knowledge graph (node counts, relationship counts).
    Use to understand the graph structure and size.
    """
    try:
        driver = get_neo4j_driver()
        
        with driver.session() as session:
            # Node counts
            node_query = "MATCH (n) RETURN labels(n)[0] as type, count(n) as count ORDER BY count DESC"
            nodes = [dict(r) for r in session.run(node_query)]
            
            # Relationship counts
            rel_query = "MATCH ()-[r]->() RETURN type(r) as type, count(r) as count ORDER BY count DESC"
            rels = [dict(r) for r in session.run(rel_query)]
            
            output = "Knowledge Graph Statistics:\n\n"
            output += "Nodes:\n"
            for n in nodes:
                output += f"  - {n['type']}: {n['count']}\n"
            output += "\nRelationships:\n"
            for r in rels:
                output += f"  - {r['type']}: {r['count']}\n"
            
            return output
    
    except Exception as e:
        return f"Error getting stats: {str(e)}"

def filter_nodes_tool(node_type: str, filters: str) -> str:
    """
    Filter nodes by exact property values.
    filters should be JSON like: {"status": "paid", "totalAmount": ">1000"}
    Use for precise filtering by known values.
    """
    try:
        driver = get_neo4j_driver()
        filter_dict = json.loads(filters)
        
        # Build WHERE clause
        where_clauses = []
        params = {}
        
        for key, value in filter_dict.items():
            if isinstance(value, str) and value.startswith(">"):
                where_clauses.append(f"n.{key} > ${key}")
                params[key] = float(value[1:])
            elif isinstance(value, str) and value.startswith("<"):
                where_clauses.append(f"n.{key} < ${key}")
                params[key] = float(value[1:])
            else:
                where_clauses.append(f"n.{key} = ${key}")
                params[key] = value
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
        MATCH (n:{node_type})
        WHERE {where_clause}
        RETURN n
        LIMIT 20
        """
        
        with driver.session() as session:
            result = session.run(query, params)
            records = [dict(record["n"]) for record in result]
            
            return json.dumps(records, indent=2, default=str)
    
    except Exception as e:
        return f"Filter error: {str(e)}"

# Create AI agent with tools
def create_ai_agent():
    """Create LangGraph agent with knowledge graph tools"""
    
    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.1,
        streaming=True
    )
    
    # Define tools
    tools = [
        Tool(
            name="vector_search",
            func=vector_search_tool,
            description="Semantic search to find similar entities by meaning. Use for: 'find products like...', 'customers who...', etc."
        ),
        Tool(
            name="cypher_query",
            func=cypher_query_tool,
            description="Execute Cypher queries for graph traversals. Use for: relationships, paths, complex patterns."
        ),
        Tool(
            name="get_node_details",
            func=get_node_details_tool,
            description="Get detailed info about a specific node. Use when you have an exact node ID."
        ),
        Tool(
            name="graph_stats",
            func=graph_stats_tool,
            description="Get graph statistics. Use to understand the graph structure."
        ),
        Tool(
            name="filter_nodes",
            func=filter_nodes_tool,
            description="Filter nodes by exact property values. Use for precise filtering."
        )
    ]
    
    # Create agent with memory
    memory = MemorySaver()
    agent = create_react_agent(llm, tools, checkpointer=memory)
    
    return agent

# API Endpoints

@app.get("/")
def root():
    return {
        "service": "Knowledge Graph RAG API",
        "version": "2.0.0",
        "graph_built": graph_built,
        "endpoints": {
            "POST /build-graph": "Build knowledge graph from PostgreSQL",
            "POST /chat": "Chat with AI agent",
            "GET /health": "Health check",
            "GET /stats": "Graph statistics"
        }
    }

@app.get("/health")
def health_check():
    """Check system health"""
    status = {
        "api": "healthy",
        "neo4j": "disconnected",
        "vector_index": "not loaded",
        "graph_built": graph_built
    }
    
    try:
        driver = get_neo4j_driver()
        driver.verify_connectivity()
        status["neo4j"] = "connected"
    except:
        pass
    
    try:
        indexer = get_vector_indexer()
        if indexer.index is not None:
            status["vector_index"] = f"loaded ({indexer.index.ntotal} vectors)"
    except:
        pass
    
    return status

@app.post("/build-graph")
async def build_graph(request: BuildGraphRequest, background_tasks: BackgroundTasks):
    """
    Build knowledge graph from PostgreSQL database
    Creates schema, ontology, Neo4j graph, and FAISS vector index
    """
    global graph_built
    
    def build_pipeline(conn_string: str):
        global graph_built, vector_indexer
        
        try:
            print("Starting graph build pipeline...")
            
            # Update environment
            os.environ["DATABASE_URL"] = conn_string
            
            # 1. Extract schema
            print("1. Extracting schema...")
            result = subprocess.run(
                ["python3", "schema_extractor.py"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            if result.returncode != 0:
                raise Exception(f"Schema extraction failed: {result.stderr}")
            
            # 2. Generate ontology
            print("2. Generating ontology...")
            result = subprocess.run(
                ["python3", "schema_to_ontology.py"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            if result.returncode != 0:
                raise Exception(f"Ontology generation failed: {result.stderr}")
            
            # 3. Build Neo4j graph
            print("3. Building Neo4j graph...")
            result = subprocess.run(
                ["python3", "create_knowledge_graph.py", "--auto"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            if result.returncode != 0:
                raise Exception(f"Graph creation failed: {result.stderr}")
            
            # 4. Build FAISS vector index
            print("4. Building vector index...")
            indexer = VectorIndexer()
            neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            neo4j_user = os.getenv("NEO4J_USER", "neo4j")
            neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
            
            indexer.build_index_from_neo4j(neo4j_uri, neo4j_user, neo4j_password)
            indexer.save_index()
            
            # Update global state
            vector_indexer = indexer
            graph_built = True
            
            print("✓ Graph build pipeline completed successfully!")
            
        except Exception as e:
            print(f"✗ Error in build pipeline: {e}")
            graph_built = False
    
    # Run in background
    background_tasks.add_task(build_pipeline, request.connection_string)
    
    return {
        "status": "success",
        "message": "Knowledge graph build started in background",
        "next_steps": [
            "1. Monitor progress at GET /health endpoint",
            "2. Once graph_built=true, use POST /chat endpoint to query",
            "3. Example: POST /chat with {\"query\": \"How many customers?\", \"stream\": false}"
        ],
        "estimated_time": "30-60 seconds for small databases",
        "endpoints": {
            "health_check": "GET /health",
            "chat": "POST /chat"
        }
    }

@app.get("/stats")
def get_stats():
    """Get graph statistics"""
    try:
        stats = graph_stats_tool()
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat with AI agent
    The agent intelligently selects tools based on query complexity
    """
    
    try:
        # Create agent
        agent = create_ai_agent()
        
        # System message to guide agent
        system_prompt = """You are a knowledge graph AI assistant. You have access to tools for:
- vector_search: Semantic search for finding similar entities
- cypher_query: Graph traversals and pattern matching
- get_node_details: Detailed node information
- filter_nodes: Precise filtering by properties
- graph_stats: Graph statistics

Choose tools intelligently based on the query:
- Use vector_search for semantic/fuzzy queries
- Use cypher_query for relationships and paths
- Use filter_nodes for exact matches
- Combine tools when needed

Always explain your reasoning and cite sources."""

        full_query = f"{system_prompt}\n\nUser query: {request.query}"
        
        if request.stream:
            # Streaming response
            async def generate():
                reasoning_steps = []
                
                config = {
                    "configurable": {"thread_id": "default"},
                    "recursion_limit": 50  # Increase recursion limit
                }
                
                async for chunk in agent.astream(
                    {"messages": [("user", full_query)]},
                    config=config
                ):
                    if "agent" in chunk:
                        # Agent reasoning
                        messages = chunk["agent"].get("messages", [])
                        for msg in messages:
                            content = str(msg.content) if hasattr(msg, 'content') else str(msg)
                            if content:
                                yield f"data: {json.dumps({'type': 'reasoning', 'content': content})}\n\n"
                    
                    elif "tools" in chunk:
                        # Tool execution
                        for tool_call in chunk.get("tools", {}).get("messages", []):
                            tool_name = getattr(tool_call, 'name', 'unknown')
                            yield f"data: {json.dumps({'type': 'tool', 'tool': tool_name})}\n\n"
                
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        
        else:
            # Non-streaming response
            config = {
                "configurable": {"thread_id": "default"},
                "recursion_limit": 50  # Increase recursion limit
            }
            result = await agent.ainvoke(
                {"messages": [("user", full_query)]},
                config=config
            )
            
            messages = result.get("messages", [])
            final_response = messages[-1].content if messages else "No response"
            
            # Ensure response is a string
            if isinstance(final_response, list):
                final_response = "\n".join(str(item) for item in final_response)
            
            # Extract tool usage and reasoning from messages
            tools_used = []
            reasoning_steps = []
            all_sources = []
            
            for msg in messages:
                # Track tool calls from AI messages
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.get('name', 'unknown')
                        if tool_name not in tools_used:
                            tools_used.append(tool_name)
                            reasoning_steps.append(f"Using tool: {tool_name}")
                
                # Track AI reasoning steps
                if hasattr(msg, 'type'):
                    if msg.type == 'ai' and hasattr(msg, 'content'):
                        content = str(msg.content)
                        if content and len(content) > 20 and content != str(final_response):
                            # Only add if it's meaningful reasoning, not the final answer
                            reasoning_steps.append(content[:200] + "..." if len(content) > 200 else content)
                    
                    # Track tool outputs
                    elif msg.type == 'tool' and hasattr(msg, 'content'):
                        tool_name = getattr(msg, 'name', 'unknown_tool')
                        tool_content = str(msg.content)
                        all_sources.append({
                            "tool": tool_name,
                            "content": tool_content,
                            "is_error": "Error:" in tool_content or "error" in tool_content.lower()[:100]
                        })
            
            # Filter sources: only keep successful tool outputs (no errors)
            # Prefer the last successful tool call as it likely provided the answer
            successful_sources = [s for s in all_sources if not s['is_error']]
            
            # Only include the last successful source (the one that provided the answer)
            final_sources = []
            if successful_sources:
                last_source = successful_sources[-1]
                content = last_source['content']
                final_sources = [{
                    "tool": last_source['tool'],
                    "content": content[:300] + "..." if len(content) > 300 else content
                }]
            
            return ChatResponse(
                response=str(final_response),
                reasoning=reasoning_steps if reasoning_steps else ["Query processed by AI agent"],
                tools_used=tools_used if tools_used else ["direct_response"],
                sources=final_sources
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
def shutdown():
    """Clean up resources"""
    global neo4j_driver
    if neo4j_driver:
        neo4j_driver.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

