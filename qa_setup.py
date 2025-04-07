'''
Takes a text file of relations triples (relations.txt),
establishes a connection to a Neo4j database, and creates a Neo4j graph.

USAGE:
   python qa_setup.py relations.txt
'''

import os
import sys
import re
from langchain_neo4j import Neo4jGraph

# Get environment variables for Neo4j
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "neo4j_password"

# Create a knowledge graph from a text file of relations

# Convert each relation to a Cypher command
def process_relation(line):
    '''
    Converts a line from a file with format (a) -[:RELATION]-> (b)
    into a Cypher command to add the relation to a graph
    '''
    match = re.match(r"\((.*?)\)\s*-\[:(.*?)\]->\s*\((.*?)\)", line.strip())
    if match:
        node1, relation, node2 = match.groups()
        query = f"""
        MERGE (a:Node {{name: '{node1}'}})
        MERGE (b:Node {{name: '{node2}'}})
        MERGE (a)-[:{relation}]->(b);
        """
        return query
    return None

# Build the Neo4j graph database from a relations text file
# by executing Cypher queries based on relations to build a Neo4j graph
def execute_cypher_file(file_path):
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")

    graph = Neo4jGraph(url=uri, username=user, password=password)

    with open(file_path, 'r') as file:
        for line in file:
            query = process_relation(line)
            if query:
                graph.query(query)
    graph.close()

    return graph

# Main
def main():
    # File containing relations for the graph should be input as the first arg
    # in the command line
    relations_file = sys.argv[1] 

    # Build graph using a plain text file of relations
    execute_cypher_file(relations_file)

# Run the script
if __name__ == "__main__":
    main()