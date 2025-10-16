import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def load_schema(schema_file="schema_output.json"):
    """Load the database schema from JSON file"""
    try:
        with open(schema_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading schema file: {e}")
        return None

def create_ontology_prompt(schema):
    """Create a detailed prompt for Gemini to generate ontology"""
    
    prompt = f"""You are an expert in database schema analysis and ontology creation for Neo4j graph databases.

I have a database schema with the following structure:

**Tables ({len(schema['tables'])} total):**
"""
    
    # Add table information
    for table_name, table_info in schema['tables'].items():
        prompt += f"\n- **{table_name}** (CSV: {table_info['csv_file']})\n"
        prompt += f"  Columns: "
        cols = [f"{col['name']} ({col['type']}{'*' if col['pk'] else ''})" for col in table_info['columns']]
        prompt += ", ".join(cols[:5])  # Show first 5 columns
        if len(cols) > 5:
            prompt += f", ... and {len(cols) - 5} more"
        prompt += "\n"
    
    # Add foreign key information
    prompt += f"\n**Foreign Key Relationships ({len(schema['foreign_keys'])} total):**\n"
    for fk in schema['foreign_keys']:
        prompt += f"- {fk['from_table']}.{fk['from_column']} → {fk['to_table']}.{fk['to_column']} (CSV: {fk['csv_file']})\n"
    
    # Add implicit relationships
    if schema['implicit_relationships']:
        prompt += f"\n**Implicit Relationships ({len(schema['implicit_relationships'])} total):**\n"
        for rel in schema['implicit_relationships']:
            prompt += f"- {rel['from_table']}.{rel['from_column']} → {rel['to_table']}.{rel['to_column']} ({rel['overlap_percentage']}% match, CSV: {rel['csv_file']})\n"
    
    # Add the task description
    prompt += """

**Task:** Create a Neo4j-compatible ontology from this database schema.

**Output Requirements:**
1. Create meaningful node classes from tables (use singular, capitalized names like "Customer" instead of "customers")
2. Define edges (relationships) based on foreign keys and implicit relationships
3. Use business-friendly relationship names (e.g., "PURCHASED", "BELONGS_TO", "CONTAINS")
4. Include the CSV file references for both nodes and edges
5. Map important columns to properties

**Output Format (JSON only, no explanation):**
```json
{
  "nodes": [
    {
      "class": "NodeClassName",
      "table": "source_table_name",
      "csv_file": "table_name.csv",
      "properties": [
        {"column": "id", "property": "nodeId", "type": "bigint", "is_key": true},
        {"column": "name", "property": "nodeName", "type": "text", "is_key": false}
      ]
    }
  ],
  "edges": [
    {
      "relationship": "RELATIONSHIP_NAME",
      "from_node": "FromNodeClass",
      "from_table": "source_table",
      "to_node": "ToNodeClass",
      "to_table": "target_table",
      "via_column": "foreign_key_column",
      "csv_file": "relationship_csv_file.csv",
      "type": "foreign_key or implicit"
    }
  ]
}
```

**Guidelines:**
- Node class names should be business entities (Customer, Product, Order, Category, etc.)
- Relationship names should be verbs in UPPERCASE (PURCHASED, PLACED, BELONGS_TO, HAS, CONTAINS, etc.)
- Include all tables as nodes
- Include all foreign key relationships and implicit relationships as edges
- For each node, map the most important columns to properties (at minimum: primary key, names, identifiers, important attributes)
- Ensure the ontology is complete and ready for Neo4j import

Generate the ontology JSON now:"""

    return prompt

def generate_ontology_with_gemini(schema):
    """Use Gemini to generate ontology from schema"""
    
    # Configure Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        return None
    
    genai.configure(api_key=api_key)
    
    # Create the model - using gemini-2.5-flash (fast and capable)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # Generate prompt
    prompt = create_ontology_prompt(schema)
    
    print("Sending schema to Gemini for ontology generation...")
    print("=" * 60)
    
    try:
        # Generate content
        response = model.generate_content(prompt)
        
        print("Received response from Gemini!")
        print("=" * 60)
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        elif response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove trailing ```
        
        response_text = response_text.strip()
        
        # Parse JSON
        ontology = json.loads(response_text)
        
        return ontology
        
    except Exception as e:
        print(f"Error generating ontology: {e}")
        print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
        return None

def save_ontology(ontology, output_file="ontology_output.json"):
    """Save the generated ontology to a JSON file"""
    try:
        with open(output_file, 'w') as f:
            json.dump(ontology, f, indent=2)
        print(f"\nOntology saved to: {output_file}")
        return True
    except Exception as e:
        print(f"Error saving ontology: {e}")
        return False

def main():
    print("Schema to Ontology Converter")
    print("=" * 60)
    
    # Load schema
    schema = load_schema()
    if not schema:
        return
    
    print(f"Loaded schema with {len(schema['tables'])} tables")
    
    # Generate ontology using Gemini
    ontology = generate_ontology_with_gemini(schema)
    
    if ontology:
        # Display the ontology
        print("\nGenerated Ontology:")
        print("=" * 60)
        print(json.dumps(ontology, indent=2))
        
        # Save to file
        save_ontology(ontology)
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY:")
        print(f"  - Nodes: {len(ontology.get('nodes', []))}")
        print(f"  - Edges: {len(ontology.get('edges', []))}")
    else:
        print("Failed to generate ontology")

if __name__ == "__main__":
    main()

