"""
Comprehensive demo of the RAG Knowledge Graph system
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70 + "\n")

def query_agent(question):
    """Send a query to the AI agent"""
    print(f"❓ Query: {question}\n")
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"query": question, "stream": False}
    )
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"💡 Answer: {result.get('response', 'No response')}\n")
        print(f"⏱️  Response time: {elapsed:.2f}s\n")
    else:
        print(f"❌ Error: {response.text}\n")

def main():
    print_section("🚀 RAG KNOWLEDGE GRAPH SYSTEM DEMO")
    
    # 1. Check system health
    print_section("1️⃣  System Health Check")
    health = requests.get(f"{BASE_URL}/health").json()
    print(json.dumps(health, indent=2))
    
    # 2. Get graph statistics
    print_section("2️⃣  Graph Statistics")
    stats = requests.get(f"{BASE_URL}/stats").json()
    print(stats['stats'])
    
    # 3. Test semantic search (vector similarity)
    print_section("3️⃣  Semantic Search (FAISS Vector Search)")
    query_agent("Find products related to wireless audio devices")
    
    # 4. Test simple counting
    print_section("4️⃣  Simple Aggregation Query")
    query_agent("How many customers do we have in total?")
    
    # 5. Test entity lookup
    print_section("5️⃣  Entity Details Lookup")
    query_agent("Tell me about customer Aisha Khan")
    
    # 6. Test relationship traversal
    print_section("6️⃣  Relationship Traversal")
    query_agent("What products has customer Ravi Patel ordered?")
    
    # 7. Test filtering
    print_section("7️⃣  Logical Filtering")
    query_agent("Show me orders with status 'pending'")
    
    # 8. Test complex graph query
    print_section("8️⃣  Complex Graph Traversal")
    query_agent("Which customers have bought products from the Electronics category?")
    
    # 9. Test aggregation
    print_section("9️⃣  Aggregation and Analysis")
    query_agent("What is the total value of all orders?")
    
    # 10. Test recommendation-like query
    print_section("🔟 Semantic Recommendation")
    query_agent("Find products similar to smartphones")
    
    print_section("✅ DEMO COMPLETED SUCCESSFULLY")
    
    print("\n📚 System Capabilities:")
    print("  ✓ Semantic search using FAISS vector embeddings")
    print("  ✓ Graph traversal using Neo4j Cypher")
    print("  ✓ Logical filtering by properties")
    print("  ✓ Dynamic tool selection by AI agent")
    print("  ✓ Reasoning chain with LangGraph")
    print("  ✓ Powered by Gemini LLM\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")

