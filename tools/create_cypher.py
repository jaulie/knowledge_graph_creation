'''
Transforms a question into a Cypher query and answers the question.

USAGE:
   python create_cypher.py json_filepath
'''

import os
import sys
import json
import spacy
from langchain_neo4j import Neo4jGraph
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_ollama import ChatOllama

class HealthcareKGQA:
    def __init__(self, uri, user, password):
        self.driver = Neo4jGraph(uri, auth=(user, password)).driver
        self.nlp = spacy.load("en_core_web_sm")  # Load once here
        self.llm = ChatOllama(model="llama3.2", temperature=0) # LLM to be used for querying the graph

    def close(self):
        self.driver.close()

    def extract_entities(self, question):
        doc = self.nlp(question)
        return [chunk.text.strip().title() for chunk in doc.noun_chunks]

    def classify_question_type(self, question):
        '''
        Classifies the question using LLM.
        '''

        template = """
        You are a helpful medical assistant that classifies user queries into one of the following categories:
        - comparison: if the user is asking if something is a better or more suitable option
        - causal: if the user is asking about the potential for a causal relationship
        - effectiveness: if the user is asking if something is an effective option, treatment, or strategy
        - association: if the user is asking if two things are in some way associated or related
        - other: if the user's query cannot possibly fit into any of the above categories

        Based on the meaning and intent of the query, assign the most appropriate category. Please return only
        the string corresponding to the category name.

        Query: {question}

        Category:"""

        prompt = PromptTemplate(
        input_variables=["question"],
        template=template,
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)

        response = chain.run(query=question)

        return response

    def generate_cypher(self, entities, qtype) -> str:
        '''
        Generates a Cypher query from a question type and a pair of entities. Question type (qtype)
        is determined by classify_question_type()
        '''

        if len(entities) == 1:
            return None
        e1, e2 = entities[0], entities[1]

        if qtype == "comparison":
            return f"""
            MATCH (a {{name: '{e1}'}})-[r:IS_BETTER_THAN|HAS_BETTER_RESULTS_THAN|IS_MORE_EFFECTIVE_THAN|IS_AS_EFFECTIVE_AS|IMPROVES|TREATS|ENHANCES]->(b {{name: '{e2}'}})
            RETURN a.name AS better, type(r) AS relation, b.name AS worse
            UNION
            MATCH (a {{name: '{e2}'}})<-[r:IS_BETTER_THAN|HAS_BETTER_RESULTS_THAN|IS_MORE_EFFECTIVE_THAN|IS_AS_EFFECTIVE_AS|IMPROVES|TREATS|ENHANCES]-(b {{name: '{e1}'}})
            RETURN b.name AS better, type(r) AS relation, a.name AS worse
            """

        elif qtype == "causal":
            return f"""
            MATCH (a {{name: '{e1}'}})-[r:CAUSES|INCREASES_RISK_OF|REDUCES_RISK_OF|PREDISPOSES_TO|IS_A_RISK_FACTOR_FOR|WORSENS|IMPROVES]->(b {{name: '{e2}'}})
            RETURN a.name AS cause, type(r) AS relation, b.name AS effect
            UNION
            MATCH (a {{name: '{e2}'}})<-[r:CAUSES|INCREASES_RISK_OF|REDUCES_RISK_OF|PREDISPOSES_TO|IS_A_RISK_FACTOR_FOR|WORSENS|IMPROVES]-(b {{name: '{e1}'}})
            RETURN b.name AS cause, type(r) AS relation, a.name AS effect
            """

        elif qtype == "effectiveness":
            return f"""
            MATCH (a {{name: '{e1}'}})-[r:IS_AS_EFFECTIVE_AS|IS_MORE_EFFECTIVE_THAN|TREATS|IMPROVES|IS_SAFE_FOR|ENHANCES|FACILITATES]->(b {{name: '{e2}'}})
            RETURN a.name AS treatment1, type(r) AS relation, b.name AS treatment2
            UNION
            MATCH (a {{name: '{e2}'}})<-[r:IS_AS_EFFECTIVE_AS|IS_MORE_EFFECTIVE_THAN|TREATS|IMPROVES|IS_SAFE_FOR|ENHANCES|FACILITATES]-(b {{name: '{e1}'}})
            RETURN a.name AS treatment1, type(r) AS relation, b.name AS treatment2
            """

        elif qtype == "association":
            return f"""
            MATCH (a {{name: '{e1}'}})-[r:IS_ASSOCIATED_WITH|PREDICTS|WORSENS|IMPROVES|INFLUENCES|ENABLES|FACILITATES|CAUSES|CORRELATES_WITH]->(b {{name: '{e2}'}})
            RETURN a.name AS from_node, type(r) AS relation, b.name AS to_node
            UNION
            MATCH (a {{name: '{e2}'}})<-[r:IS_ASSOCIATED_WITH|PREDICTS|WORSENS|IMPROVES|INFLUENCES|ENABLES|FACILITATES|CAUSES|CORRELATES_WITH]-(b {{name: '{e1}'}})
            RETURN b.name AS from_node, type(r) AS relation, a.name AS to_node
            """

        else:
            return f"""
            MATCH (a)-[r]->(b)
            WHERE a.name = '{e1}' OR b.name = '{e1}' OR a.name = '{e2}' OR b.name = '{e2}'
            RETURN a.name AS from_node, type(r) AS relation, b.name AS to_node LIMIT 5
            """

    def query_kg(self, question):
        entities = self.extract_entities(question)
        qtype = self.classify_question_type(question)
        cypher = self.generate_cypher(entities, qtype)

        if not cypher:
            return ["Unable to generate query."]

        with self.driver.session() as session:
            result = session.run(cypher)
            facts = []
            for record in result:
                line = " - ".join(str(v) for v in record.values())
                facts.append(line)
            return facts


# Main
def main():

    # Get environment variables for Neo4j
    os.environ["NEO4J_URI"] = "bolt://localhost:7687"
    os.environ["NEO4J_USERNAME"] = "neo4j"
    os.environ["NEO4J_PASSWORD"] = "neo4j_password"

    # Create HealthcareKGQA object
    kgqa = HealthcareKGQA(os.environ.get("NEO4J_URI"), os.environ.get("NEO4J_USERNAME"), os.environ.get("NEO4J_PASSWORD"))

    # Go through questions  
    for q in questions[:50]:
        facts = kgqa.query_kg(q)
        print(f"\n--- Question: {q} ---")
        print("Context:")
        print("\n".join(facts))
        print("\nAnswer:")
        print(ask_llm(q, facts))
        answers.append(ask_llm(q, facts).lower().rstrip('.'))

    kgqa.close()
        
    # Create Cypher command from user query
    cypher = generate_cypher_from_query(graph, query)
    print(cypher)

    # Query graph with Cypher command
    result = graph.query(cypher)

    print(result)

# Run the script
if __name__ == "__main__":
    main()