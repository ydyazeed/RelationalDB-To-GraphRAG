import json
import os
import csv
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()

class KnowledgeGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.ontology = None
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
    
    def load_ontology(self, ontology_file="ontology_output.json"):
        """Load the ontology JSON file"""
        try:
            with open(ontology_file, 'r') as f:
                self.ontology = json.load(f)
            print(f"✓ Loaded ontology: {len(self.ontology['nodes'])} nodes, {len(self.ontology['edges'])} edges")
            return True
        except Exception as e:
            print(f"✗ Error loading ontology: {e}")
            return False
    
    def clear_database(self):
        """Clear all nodes and relationships from the database"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Database cleared")
    
    def create_constraints(self):
        """Create unique constraints for node IDs"""
        print("\nCreating constraints...")
        with self.driver.session() as session:
            for node in self.ontology['nodes']:
                node_class = node['class']
                # Find the key property (usually nodeId)
                key_property = None
                for prop in node['properties']:
                    if prop.get('is_key', False):
                        key_property = prop['property']
                        break
                
                if key_property:
                    constraint_name = f"constraint_{node_class}_{key_property}"
                    try:
                        # Drop existing constraint if it exists
                        session.run(f"DROP CONSTRAINT {constraint_name} IF EXISTS")
                        # Create new constraint
                        query = f"CREATE CONSTRAINT {constraint_name} FOR (n:{node_class}) REQUIRE n.{key_property} IS UNIQUE"
                        session.run(query)
                        print(f"  ✓ Constraint created for {node_class}.{key_property}")
                    except Exception as e:
                        print(f"  ⚠ Constraint for {node_class}.{key_property}: {e}")
    
    def load_nodes(self):
        """Load nodes from CSV files"""
        print("\nLoading nodes from CSV files...")
        
        for node in self.ontology['nodes']:
            node_class = node['class']
            csv_file = node['csv_file']
            table = node['table']
            properties = node['properties']
            
            if not os.path.exists(csv_file):
                print(f"  ✗ CSV file not found: {csv_file}")
                continue
            
            # Read CSV and create nodes
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if not rows:
                print(f"  ⚠ No data in {csv_file}")
                continue
            
            # Build property mapping
            prop_map = {prop['column']: prop['property'] for prop in properties}
            
            # Create Cypher query for batch import
            with self.driver.session() as session:
                count = 0
                for row in rows:
                    # Build properties dict
                    props = {}
                    for col, prop_name in prop_map.items():
                        if col in row and row[col]:
                            # Convert empty strings to None
                            value = row[col] if row[col] != '' else None
                            if value:
                                props[prop_name] = value
                    
                    # Create node
                    if props:
                        query = f"CREATE (n:{node_class} $props)"
                        session.run(query, props=props)
                        count += 1
                
                print(f"  ✓ Created {count} {node_class} nodes from {csv_file}")
    
    def load_relationships(self):
        """Load relationships from CSV files"""
        print("\nLoading relationships from CSV files...")
        
        for edge in self.ontology['edges']:
            relationship = edge['relationship']
            from_node = edge['from_node']
            to_node = edge['to_node']
            csv_file = edge['csv_file']
            
            if not os.path.exists(csv_file):
                print(f"  ✗ CSV file not found: {csv_file}")
                continue
            
            # Read CSV
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)  # Skip header
                rows = list(reader)
            
            if not rows:
                print(f"  ⚠ No data in {csv_file}")
                continue
            
            # Create relationships
            with self.driver.session() as session:
                count = 0
                for row in rows:
                    if len(row) >= 2 and row[0] and row[1]:
                        from_value = row[0]
                        to_value = row[1]
                        
                        # Match nodes and create relationship
                        query = f"""
                        MATCH (a:{from_node})
                        MATCH (b:{to_node})
                        WHERE a.nodeId = $from_value AND b.nodeId = $to_value
                        MERGE (a)-[r:{relationship}]->(b)
                        """
                        
                        try:
                            session.run(query, from_value=from_value, to_value=to_value)
                            count += 1
                        except Exception as e:
                            # Try with sku if nodeId doesn't match
                            if 'sku' in csv_file.lower():
                                query = f"""
                                MATCH (a:{from_node})
                                MATCH (b:{to_node})
                                WHERE a.sku = $from_value AND b.sku = $to_value
                                MERGE (a)-[r:{relationship}]->(b)
                                """
                                try:
                                    session.run(query, from_value=from_value, to_value=to_value)
                                    count += 1
                                except:
                                    pass
                
                print(f"  ✓ Created {count} {relationship} relationships from {csv_file}")
    
    def run_test_queries(self):
        """Run various test queries to verify the knowledge graph"""
        print("\n" + "="*70)
        print("TESTING KNOWLEDGE GRAPH WITH CYPHER QUERIES")
        print("="*70)
        
        with self.driver.session() as session:
            # Test 1: Count all nodes
            print("\n1. Count all nodes by type:")
            query = """
            MATCH (n)
            RETURN labels(n)[0] as NodeType, count(n) as Count
            ORDER BY Count DESC
            """
            result = session.run(query)
            for record in result:
                print(f"   {record['NodeType']}: {record['Count']}")
            
            # Test 2: Count all relationships
            print("\n2. Count all relationships by type:")
            query = """
            MATCH ()-[r]->()
            RETURN type(r) as RelationType, count(r) as Count
            ORDER BY Count DESC
            """
            result = session.run(query)
            for record in result:
                print(f"   {record['RelationType']}: {record['Count']}")
            
            # Test 3: Find customers and their orders
            print("\n3. Sample: Customers and their orders:")
            query = """
            MATCH (c:Customer)-[:PLACED]->(o:Order)
            RETURN c.firstName as Customer, c.email as Email, 
                   o.nodeId as OrderId, o.status as Status, o.totalAmount as Amount
            LIMIT 5
            """
            result = session.run(query)
            for record in result:
                print(f"   {record['Customer']} ({record['Email']}): Order #{record['OrderId']} - {record['Status']} - ${record['Amount']}")
            
            # Test 4: Products in orders
            print("\n4. Sample: Products in orders with customer info:")
            query = """
            MATCH (c:Customer)-[:PLACED]->(o:Order)-[:HAS_ITEM]->(oi:OrderItem)-[:FOR_PRODUCT]->(p:Product)
            RETURN c.firstName as Customer, o.nodeId as OrderId, 
                   p.name as Product, oi.quantity as Quantity, oi.unitPrice as Price
            LIMIT 5
            """
            result = session.run(query)
            for record in result:
                print(f"   {record['Customer']}'s Order #{record['OrderId']}: {record['Quantity']}x {record['Product']} @ ${record['Price']}")
            
            # Test 5: Products by category
            print("\n5. Products by category:")
            query = """
            MATCH (p:Product)-[:BELONGS_TO_CATEGORY]->(c:Category)
            RETURN c.name as Category, collect(p.name) as Products, count(p) as Count
            ORDER BY Count DESC
            """
            result = session.run(query)
            for record in result:
                products = record['Products'][:3]  # Show first 3
                print(f"   {record['Category']} ({record['Count']}): {', '.join(products)}{'...' if record['Count'] > 3 else ''}")
            
            # Test 6: Implicit relationship - Product hierarchy
            print("\n6. Product hierarchy (implicit relationship):")
            query = """
            MATCH (p:Product)-[:HAS_PARENT]->(parent:Product)
            RETURN p.sku as ChildSKU, parent.sku as ParentSKU
            LIMIT 5
            """
            result = session.run(query)
            count = 0
            for record in result:
                print(f"   {record['ChildSKU']} → {record['ParentSKU']}")
                count += 1
            if count == 0:
                print("   (No product hierarchy relationships found)")
            
            # Test 7: Customer order statistics
            print("\n7. Top customers by total spending:")
            query = """
            MATCH (c:Customer)-[:PLACED]->(o:Order)
            WITH c, sum(toFloat(o.totalAmount)) as TotalSpent, count(o) as OrderCount
            RETURN c.firstName + ' ' + c.lastName as Customer, 
                   OrderCount, TotalSpent
            ORDER BY TotalSpent DESC
            LIMIT 5
            """
            result = session.run(query)
            for record in result:
                print(f"   {record['Customer']}: {record['OrderCount']} orders, ${record['TotalSpent']:.2f} total")
            
            # Test 8: Graph statistics
            print("\n8. Overall graph statistics:")
            query = """
            MATCH (n)
            WITH count(n) as NodeCount
            MATCH ()-[r]->()
            RETURN NodeCount, count(r) as RelationshipCount
            """
            result = session.run(query)
            record = result.single()
            print(f"   Total Nodes: {record['NodeCount']}")
            print(f"   Total Relationships: {record['RelationshipCount']}")

def main():
    print("="*70)
    print("NEO4J KNOWLEDGE GRAPH BUILDER")
    print("="*70)
    
    # Load Neo4j credentials
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    print(f"\nConnecting to Neo4j at {uri}...")
    
    try:
        # Create builder instance
        builder = KnowledgeGraphBuilder(uri, user, password)
        
        # Test connection
        with builder.driver.session() as session:
            result = session.run("RETURN 1 as test")
            result.single()
        print("✓ Connected to Neo4j successfully!")
        
        # Load ontology
        if not builder.load_ontology():
            return
        
        # Ask to clear database (skip if --auto flag is provided)
        if '--auto' not in sys.argv:
            print("\n⚠  This will clear the existing database and rebuild it.")
            response = input("Continue? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("Aborted.")
                return
        else:
            print("\n⚠  Auto mode: Clearing and rebuilding database...")
        
        # Build knowledge graph
        print("\nBuilding knowledge graph...")
        builder.clear_database()
        builder.create_constraints()
        builder.load_nodes()
        builder.load_relationships()
        
        # Run test queries
        builder.run_test_queries()
        
        print("\n" + "="*70)
        print("✓ KNOWLEDGE GRAPH CREATED SUCCESSFULLY!")
        print("="*70)
        print("\nYou can now query your graph using Neo4j Browser at:")
        print(f"  {uri.replace('bolt://', 'http://').replace(':7687', ':7474')}")
        
        # Close connection
        builder.close()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure Neo4j is running and credentials are correct in .env file")
        return

if __name__ == "__main__":
    main()

