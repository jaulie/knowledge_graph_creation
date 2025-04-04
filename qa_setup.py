'''
Takes a text file of relations triples and establishes a connection to a Neo4j database. 
Then transforms a question into a Cypher query and answers the question.

USAGE:
   python qa_setup.py relations.txt
'''

import os
import sys
import re
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_neo4j import Neo4jVector
from operator import add
from typing import Annotated, List
from typing_extensions import TypedDict

os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "neo4j_password"

# LLM to be used for querying the graph
llm = ChatOllama(model="llama3.1", temperature=0)

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

# TODO: Implement guardrails, ensuring that the user's query is relevant

# TODO: Provide a few examples for few-shot system
examples = [
    {
        "question": "Is naturopathy as effective as conventional therapy for treatment of menopausal symptoms?",
        "query": "MATCH ",
    },{
        "question": "Can randomised trials rely on existing electronic data?",
        "query": "",
    },{
        "question": "Is laparoscopic radical prostatectomy better than traditional retropubic radical prostatectomy?",
        "query": "",
    },{
        "question": "Does bacterial gastroenteritis predispose people to functional gastrointestinal disorders?",
        "query": "",
    },{
        "question": "Is early colonoscopy after admission for acute diverticular bleeding needed?",
        "query": "",
    }
]

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples, OllamaEmbeddings(model="llama3.1"), Neo4jVector, k=5, input_keys=["question"]
)

# Function to create chain that generates few-shot Cypher queries from question
text2cypher_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system", # 'system' message sets rules for LLM's behavior, ensuring strict formatting rules
            (
                "Given an input question, convert it to a Cypher query. No pre-amble."
                "Do not wrap the response in any backticks or anything else. Respond with a Cypher statement only!"
            ),
        ),
        (
            "human", 
            (
                """You are a Neo4j expert. Given an input question, create a syntactically correct Cypher query to run.
Do not wrap the response in any backticks or anything else. Respond with a Cypher statement only!
Here is the schema information
{schema}

Below are a number of examples of questions and their corresponding Cypher queries.

{fewshot_examples}

User input: {question}
Cypher query:"""
            ),
        ),
    ]
)

# Creates a chain with prompt, llm, and StrOutputParser()
text2cypher_chain = text2cypher_prompt | llm | StrOutputParser()

def generate_cypher_from_query(graph: Neo4jGraph, question: str) -> str:
    """
    Generates a cypher statement based on the provided few-shot examples, schema, and user input.
    Returns a string which is the Cypher query. 
    """
    NL = "\n"
    fewshot_examples = (NL * 2).join(
        [
            f"Question: {el['question']}{NL}Cypher:{el['query']}"
            for el in example_selector.select_examples(
                {"question": question}
            )
        ]
    )
    generated_cypher = text2cypher_chain.invoke(
        {
            "question": question,
            "fewshot_examples": fewshot_examples,
            "schema": graph.schema,
        }
    )
    return generated_cypher

# Main
def main():
    # File containing relations for the graph should be input as the first arg
    # in the command line
    relations_file = sys.argv[1] 

    # Build graph using a plain text file of relations
    graph = execute_cypher_file(relations_file)

    # Retrieve query from user
    query = input("Please enter your question for the knowledge graph: ")
        
    # Create Cypher command from user query
    cypher = generate_cypher_from_query(graph, query)
    print(cypher)

    # Query graph with Cypher command
    result = graph.query(cypher)

    print(result)

# Run the script
if __name__ == "__main__":
    main()