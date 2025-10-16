"""
Test script for the RAG API system
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2))
    print()

def test_stats():
    """Test stats endpoint"""
    print("="*70)
    print("TEST 2: Graph Statistics")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/stats")
    print(response.json()['stats'])
    print()

def test_chat_simple():
    """Test chat endpoint with simple query"""
    print("="*70)
    print("TEST 3: Simple AI Chat Query")
    print("="*70)
    
    query = "How many customers do we have?"
    
    print(f"Query: {query}\n")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"query": query, "stream": False}
    )
    
    result = response.json()
    print(f"Response: {result['response']}\n")

def test_chat_semantic():
    """Test chat with semantic search"""
    print("="*70)
    print("TEST 4: Semantic Search Query")
    print("="*70)
    
    query = "Find products related to wireless audio"
    
    print(f"Query: {query}\n")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"query": query, "stream": False}
    )
    
    result = response.json()
    print(f"Response: {result['response']}\n")

def test_chat_complex():
    """Test chat with complex graph traversal"""
    print("="*70)
    print("TEST 5: Complex Graph Query")
    print("="*70)
    
    query = "Show me customers who have placed orders with more than 2 items"
    
    print(f"Query: {query}\n")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"query": query, "stream": False}
    )
    
    result = response.json()
    print(f"Response: {result['response']}\n")

def test_chat_relationship():
    """Test chat with relationship query"""
    print("="*70)
    print("TEST 6: Relationship Query")
    print("="*70)
    
    query = "What products has customer Aisha Khan ordered?"
    
    print(f"Query: {query}\n")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"query": query, "stream": False}
    )
    
    result = response.json()
    print(f"Response: {result['response']}\n")

def main():
    print("\n")
    print("="*70)
    print("RAG API SYSTEM TEST")
    print("="*70)
    print()
    
    try:
        test_health()
        test_stats()
        test_chat_simple()
        test_chat_semantic()
        test_chat_complex()
        test_chat_relationship()
        
        print("="*70)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    main()

