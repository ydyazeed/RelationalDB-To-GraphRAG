"""
Vector Embedding and FAISS Indexing for Knowledge Graph Nodes
"""

import os
import json
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
from dotenv import load_dotenv
from typing import List, Dict, Tuple

load_dotenv()

class VectorIndexer:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """Initialize with sentence transformer model"""
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.node_metadata = []  # Store node info for retrieval
        
    def create_node_text(self, node_type: str, props: Dict) -> str:
        """Create text representation for embedding"""
        if node_type == "Product":
            return f"Product: {props.get('name', '')}. SKU: {props.get('sku', '')}. Price: ${props.get('unitPrice', '')}. Category: {props.get('category', 'N/A')}"
        
        elif node_type == "Customer":
            return f"Customer: {props.get('firstName', '')} {props.get('lastName', '')}. Email: {props.get('email', '')}. Phone: {props.get('phone', 'N/A')}"
        
        elif node_type == "Order":
            return f"Order #{props.get('nodeId', '')}. Status: {props.get('status', '')}. Total: ${props.get('totalAmount', '')}. Date: {props.get('orderDate', '')}"
        
        elif node_type == "Category":
            return f"Category: {props.get('name', '')}. Description: {props.get('description', '')}"
        
        elif node_type == "OrderItem":
            return f"Order item. Quantity: {props.get('quantity', '')}. Unit price: ${props.get('unitPrice', '')}. Total: ${props.get('lineTotal', '')}"
        
        else:
            return " ".join([f"{k}: {v}" for k, v in props.items() if isinstance(v, (str, int, float))])
    
    def build_index_from_neo4j(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        """Build FAISS index from all nodes in Neo4j"""
        print("\n🔍 Building FAISS index from Neo4j...")
        
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        all_texts = []
        all_embeddings = []
        
        try:
            with driver.session() as session:
                # Get all node labels
                labels_result = session.run("CALL db.labels()")
                node_types = [record["label"] for record in labels_result]
                
                print(f"  Found node types: {', '.join(node_types)}")
                
                for node_type in node_types:
                    print(f"  Processing {node_type} nodes...")
                    
                    # Get all nodes of this type
                    query = f"MATCH (n:{node_type}) RETURN n"
                    result = session.run(query)
                    
                    for record in result:
                        node = record["n"]
                        props = dict(node)
                        
                        # Create text representation
                        text = self.create_node_text(node_type, props)
                        
                        # Store metadata
                        self.node_metadata.append({
                            "type": node_type,
                            "id": props.get("nodeId", props.get("id", "")),
                            "text": text,
                            "properties": props
                        })
                        
                        all_texts.append(text)
                
                print(f"  Total nodes: {len(all_texts)}")
                
                # Generate embeddings
                print("  Generating embeddings...")
                all_embeddings = self.model.encode(all_texts, show_progress_bar=True)
                
                # Build FAISS index
                print("  Building FAISS index...")
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine similarity)
                
                # Normalize vectors for cosine similarity
                faiss.normalize_L2(all_embeddings)
                self.index.add(all_embeddings)
                
                print(f"  ✓ FAISS index built with {self.index.ntotal} vectors")
                
        finally:
            driver.close()
    
    def save_index(self, index_path="faiss_index.bin", metadata_path="index_metadata.pkl"):
        """Save FAISS index and metadata to disk"""
        if self.index is None:
            raise ValueError("No index to save. Build index first.")
        
        faiss.write_index(self.index, index_path)
        
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'metadata': self.node_metadata,
                'dimension': self.dimension
            }, f)
        
        print(f"  ✓ Index saved to {index_path}")
        print(f"  ✓ Metadata saved to {metadata_path}")
    
    def load_index(self, index_path="faiss_index.bin", metadata_path="index_metadata.pkl"):
        """Load FAISS index and metadata from disk"""
        self.index = faiss.read_index(index_path)
        
        with open(metadata_path, 'rb') as f:
            data = pickle.load(f)
            self.node_metadata = data['metadata']
            self.dimension = data['dimension']
        
        print(f"  ✓ Index loaded with {self.index.ntotal} vectors")
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar nodes using vector similarity"""
        if self.index is None:
            raise ValueError("No index loaded. Build or load index first.")
        
        # Generate query embedding
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        distances, indices = self.index.search(query_embedding, k)
        
        # Return results
        results = []
        for i, (idx, dist) in enumerate(zip(indices[0], distances[0])):
            if idx < len(self.node_metadata):
                result = self.node_metadata[idx].copy()
                result['similarity_score'] = float(dist)
                result['rank'] = i + 1
                results.append(result)
        
        return results

def main():
    """Test the vector indexer"""
    print("="*70)
    print("VECTOR INDEXER - FAISS")
    print("="*70)
    
    # Initialize
    indexer = VectorIndexer()
    
    # Build index from Neo4j
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    
    indexer.build_index_from_neo4j(neo4j_uri, neo4j_user, neo4j_password)
    
    # Save index
    indexer.save_index()
    
    # Test search
    print("\n" + "="*70)
    print("TESTING VECTOR SEARCH")
    print("="*70)
    
    test_queries = [
        "wireless headphones",
        "customer email",
        "pending order"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = indexer.search(query, k=3)
        for result in results:
            print(f"  [{result['rank']}] {result['type']}: {result['text'][:80]}... (score: {result['similarity_score']:.4f})")

if __name__ == "__main__":
    main()

