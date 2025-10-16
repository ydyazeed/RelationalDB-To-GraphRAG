import psycopg
import json
import os
import csv
from dotenv import load_dotenv
from decimal import Decimal
from datetime import datetime, date

# Load environment variables
load_dotenv()

class SchemaExtractor:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            print("Connected to database successfully!")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def get_tables(self):
        """Get all tables in the public schema"""
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_columns(self, table_name):
        """Get all columns for a specific table"""
        query = """
            SELECT 
                c.column_name,
                c.data_type,
                c.character_maximum_length,
                c.is_nullable,
                c.column_default
            FROM information_schema.columns c
            WHERE c.table_schema = 'public' 
            AND c.table_name = %s
            ORDER BY c.ordinal_position;
        """
        self.cursor.execute(query, (table_name,))
        return self.cursor.fetchall()
    
    def get_primary_keys(self, table_name):
        """Get primary key columns for a table"""
        query = """
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass
            AND i.indisprimary;
        """
        self.cursor.execute(query, (f'public.{table_name}',))
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_foreign_keys(self):
        """Get all foreign key relationships in the database"""
        query = """
            SELECT
                tc.table_name AS from_table,
                kcu.column_name AS from_column,
                ccu.table_name AS to_table,
                ccu.column_name AS to_column,
                tc.constraint_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_sample_rows(self, table_name, limit=2):
        """Get random sample rows from a table"""
        try:
            # First check if table has any rows
            count_query = f'SELECT COUNT(*) FROM "{table_name}";'
            self.cursor.execute(count_query)
            row_count = self.cursor.fetchone()[0]
            
            if row_count == 0:
                return []
            
            # Limit sample size to available rows
            sample_size = min(limit, row_count)
            
            # Get random sample
            query = f'SELECT * FROM "{table_name}" ORDER BY RANDOM() LIMIT {sample_size};'
            self.cursor.execute(query)
            
            # Get column names
            colnames = [desc[0] for desc in self.cursor.description]
            
            # Convert rows to dictionaries
            rows = []
            for row in self.cursor.fetchall():
                row_dict = {}
                for i, val in enumerate(row):
                    # Convert non-JSON-serializable types
                    if isinstance(val, Decimal):
                        row_dict[colnames[i]] = float(val)
                    elif isinstance(val, (datetime, date)):
                        row_dict[colnames[i]] = val.isoformat()
                    elif isinstance(val, bytes):
                        row_dict[colnames[i]] = val.hex()
                    else:
                        row_dict[colnames[i]] = val
                rows.append(row_dict)
            
            return rows
        except Exception as e:
            print(f"Error getting sample rows from {table_name}: {e}")
            return []
    
    def export_table_to_csv(self, table_name):
        """Export all rows from a table to CSV file"""
        try:
            csv_filename = f"{table_name}.csv"
            
            # Get all rows from table
            query = f'SELECT * FROM "{table_name}";'
            self.cursor.execute(query)
            
            # Get column names
            colnames = [desc[0] for desc in self.cursor.description]
            
            # Write to CSV
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(colnames)  # Header
                
                for row in self.cursor.fetchall():
                    # Convert values for CSV
                    csv_row = []
                    for val in row:
                        if isinstance(val, Decimal):
                            csv_row.append(float(val))
                        elif isinstance(val, (datetime, date)):
                            csv_row.append(val.isoformat())
                        elif isinstance(val, bytes):
                            csv_row.append(val.hex())
                        elif val is None:
                            csv_row.append('')
                        else:
                            csv_row.append(val)
                    writer.writerow(csv_row)
            
            return csv_filename
        except Exception as e:
            print(f"Error exporting {table_name} to CSV: {e}")
            return None
    
    def export_relationship_to_csv(self, from_table, from_column, to_table, to_column, relationship_type="fk"):
        """Export foreign key or implicit relationship data to CSV"""
        try:
            csv_filename = f"{relationship_type}_{from_table}_{from_column}_to_{to_table}_{to_column}.csv"
            
            # Query to get relationship data
            query = f'''
                SELECT 
                    t1."{from_column}" as from_value,
                    t2."{to_column}" as to_value
                FROM "{from_table}" t1
                LEFT JOIN "{to_table}" t2 ON t1."{from_column}" = t2."{to_column}"
                WHERE t1."{from_column}" IS NOT NULL
                ORDER BY t1."{from_column}";
            '''
            self.cursor.execute(query)
            
            # Write to CSV
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([f'{from_table}.{from_column}', f'{to_table}.{to_column}'])
                
                for row in self.cursor.fetchall():
                    csv_row = []
                    for val in row:
                        if isinstance(val, Decimal):
                            csv_row.append(float(val))
                        elif isinstance(val, (datetime, date)):
                            csv_row.append(val.isoformat())
                        elif isinstance(val, bytes):
                            csv_row.append(val.hex())
                        elif val is None:
                            csv_row.append('')
                        else:
                            csv_row.append(val)
                    writer.writerow(csv_row)
            
            return csv_filename
        except Exception as e:
            print(f"Error exporting relationship {from_table}.{from_column} -> {to_table}.{to_column}: {e}")
            return None
    
    def get_distinct_values(self, table_name, column_name, limit=1000):
        """Get distinct non-null values from a column (limited for performance)"""
        try:
            query = f'SELECT DISTINCT "{column_name}" FROM "{table_name}" WHERE "{column_name}" IS NOT NULL LIMIT {limit};'
            self.cursor.execute(query)
            return set(row[0] for row in self.cursor.fetchall())
        except Exception as e:
            print(f"Error getting distinct values from {table_name}.{column_name}: {e}")
            return set()
    
    def find_implicit_relationships(self, tables_info, explicit_fks, threshold=0.8):
        """Find implicit relationships by analyzing value overlap between columns"""
        implicit_relationships = []
        
        # Build a comprehensive set of relationships already covered by explicit FKs
        # Include both direct FKs and columns involved in FK relationships
        covered_columns = set()
        for fk in explicit_fks:
            # Mark these column pairs as covered
            covered_columns.add((fk[0], fk[1]))  # from_table.from_column
            covered_columns.add((fk[2], fk[3]))  # to_table.to_column
        
        # Common timestamp/audit columns to exclude
        excluded_columns = {'created_at', 'updated_at', 'deleted_at', 'modified_at', 'timestamp', 'date', 'time'}
        
        # Columns that are typically data values, not relationships
        excluded_patterns = ['price', 'amount', 'total', 'quantity', 'count', 'status', 'name', 'description', 'email', 'phone']
        
        print("\nAnalyzing implicit relationships...")
        
        # Compare columns across different tables
        table_names = list(tables_info.keys())
        for i, table1 in enumerate(table_names):
            for table2 in table_names[i+1:]:
                cols1 = tables_info[table1]['columns']
                cols2 = tables_info[table2]['columns']
                
                # Get primary key columns for table2 (potential targets)
                pk_cols2 = {col['name'] for col in cols2 if col['pk']}
                
                for col1 in cols1:
                    # Skip primary keys and audit columns
                    if col1['pk'] or col1['name'] in excluded_columns:
                        continue
                    
                    # Skip columns already in explicit FKs
                    if (table1, col1['name']) in covered_columns:
                        continue
                    
                    # Skip if column name suggests it's a data value, not a relationship
                    if any(pattern in col1['name'].lower() for pattern in excluded_patterns):
                        continue
                    
                    for col2 in cols2:
                        # Skip audit columns
                        if col2['name'] in excluded_columns:
                            continue
                        
                        # Skip if column already in explicit FKs
                        if (table2, col2['name']) in covered_columns:
                            continue
                        
                        # Skip if different types
                        if col1['type'] != col2['type']:
                            continue
                        
                        # Skip if column name suggests it's a data value
                        if any(pattern in col2['name'].lower() for pattern in excluded_patterns):
                            continue
                        
                        # Prioritize relationships to primary keys or columns with similar naming
                        is_likely_relationship = (
                            col2['pk'] or  # col2 is a primary key
                            col1['name'].endswith('_id') or col1['name'].endswith('_sku') or  # col1 looks like a foreign key
                            col1['name'] == col2['name'] or  # same column name (like 'sku' referencing 'sku')
                            col1['name'].replace('_id', '') in table2 or  # naming convention match
                            col1['name'].replace('_sku', '') in table2
                        )
                        
                        if not is_likely_relationship:
                            continue
                        
                        # Get distinct values from both columns
                        values1 = self.get_distinct_values(table1, col1['name'])
                        values2 = self.get_distinct_values(table2, col2['name'])
                        
                        if not values1 or not values2 or len(values1) < 2:
                            continue
                        
                        # Calculate overlap
                        overlap = values1.intersection(values2)
                        
                        # For implicit relationships, we want high overlap of col1 values in col2
                        # (meaning col1 is likely referencing col2)
                        overlap_ratio = len(overlap) / len(values1)
                        
                        # Require high overlap (default 80%)
                        if overlap_ratio >= threshold and len(overlap) >= 2:
                            relationship = {
                                "from_table": table1,
                                "from_column": col1['name'],
                                "to_table": table2,
                                "to_column": col2['name'],
                                "overlap_percentage": round(overlap_ratio * 100, 2),
                                "match_count": len(overlap),
                                "type": "implicit",
                                "likely_direction": f"{table1}.{col1['name']} -> {table2}.{col2['name']}"
                            }
                            
                            implicit_relationships.append(relationship)
                            print(f"  Found: {table1}.{col1['name']} -> {table2}.{col2['name']} ({overlap_ratio*100:.1f}% overlap, {len(overlap)} matches)")
        
        return implicit_relationships
    
    def extract_schema(self):
        """Extract complete database schema"""
        schema = {
            "tables": {},
            "foreign_keys": [],
            "implicit_relationships": []
        }
        
        # Get all tables
        tables = self.get_tables()
        print(f"Found {len(tables)} tables")
        
        # Process each table
        for table_name in tables:
            print(f"Processing table: {table_name}")
            
            # Get columns
            columns_data = self.get_columns(table_name)
            primary_keys = self.get_primary_keys(table_name)
            
            columns = []
            for col in columns_data:
                column_info = {
                    "name": col[0],
                    "type": col[1],
                    "nullable": col[3] == 'YES',
                    "pk": col[0] in primary_keys
                }
                
                # Add max length if applicable
                if col[2]:
                    column_info["max_length"] = col[2]
                
                # Add default value if applicable
                if col[4]:
                    column_info["default"] = col[4]
                
                columns.append(column_info)
            
            # Get sample rows
            sample_rows = self.get_sample_rows(table_name, limit=2)
            
            # Export table to CSV
            csv_file = self.export_table_to_csv(table_name)
            
            schema["tables"][table_name] = {
                "columns": columns,
                "sample_rows": sample_rows,
                "csv_file": csv_file
            }
        
        # Get foreign keys
        fk_data = self.get_foreign_keys()
        for fk in fk_data:
            # Export foreign key relationship to CSV
            csv_file = self.export_relationship_to_csv(fk[0], fk[1], fk[2], fk[3], "fk")
            
            schema["foreign_keys"].append({
                "from_table": fk[0],
                "from_column": fk[1],
                "to_table": fk[2],
                "to_column": fk[3],
                "constraint_name": fk[4],
                "csv_file": csv_file
            })
        
        # Find implicit relationships
        implicit_rels = self.find_implicit_relationships(schema["tables"], fk_data)
        
        # Export implicit relationships to CSV and add to schema
        for rel in implicit_rels:
            csv_file = self.export_relationship_to_csv(
                rel["from_table"], 
                rel["from_column"], 
                rel["to_table"], 
                rel["to_column"], 
                "implicit"
            )
            rel["csv_file"] = csv_file
        
        schema["implicit_relationships"] = implicit_rels
        
        return schema
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed")

def main():
    # Get connection string from environment variable
    connection_string = os.getenv("DATABASE_URL")
    
    if not connection_string:
        print("Error: DATABASE_URL not found in environment variables")
        return
    
    # Create extractor instance
    extractor = SchemaExtractor(connection_string)
    
    try:
        # Connect to database
        extractor.connect()
        
        # Extract schema
        print("\nExtracting database schema...")
        schema = extractor.extract_schema()
        
        # Save to JSON file
        output_file = "schema_output.json"
        with open(output_file, 'w') as f:
            json.dump(schema, f, indent=2)
        
        print(f"\nSchema extracted successfully!")
        print(f"Output saved to: {output_file}")
        print(f"\nTotal tables: {len(schema['tables'])}")
        print(f"Total foreign keys: {len(schema['foreign_keys'])}")
        print(f"Total implicit relationships: {len(schema['implicit_relationships'])}")
        
        # Print preview
        print("\n" + "="*50)
        print("SCHEMA PREVIEW:")
        print("="*50)
        print(json.dumps(schema, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main()

