# Automatically Creating Knowledge Graphs
Playing around with automatically creating knowledge graphs using LLaMa3.2 (with LangChain)

This project uses LangChain to build a Neo4j Graph DB and a QA Pipeline. We have attempted multiple approaches, all using the PubMedQA dataset, which can be found [here](https://pubmedqa.github.io/).

Prerequisites:
1. Download Ollama [here](https://ollama.com/download).   
   a. Make sure to pull the model you plan to use. See [here](https://github.com/ollama/ollama?tab=readme-ov-file) for a list of the available models.
2. Download Neo4j Desktop [here](https://neo4j.com/download/?utm_source=GSearch&utm_medium=PaidSearch&utm_campaign=Evergreen&utm_content=AMS-Search-SEMBrand-Evergreen-None-SEM-SEM-NonABM&utm_term=download%20neo4j&utm_adgroup=download&gad_source=1&gclid=CjwKCAiAn9a9BhBtEiwAbKg6fk0FJYnTAH_2YDr2LOicg7-m28Ofd6veBaMJg-7Nt83qApOLfDjNDhoCHRgQAvD_BwE)   
   a. Create a new project with a GraphDBMS and start the DBMS by pressing 'Start'.   
   b. On the righthand side, 'Reset DBMS password'. This is the password you will enter into the password field.
   c. Install APOC Plugin
3. Graph DBs are queried using the language Cypher.

How to use:
1. simple_relations_kg.ipynb builds a simple knowledge graph with only three types of relations.
2. rag_test_with_fixed_relations.ipynb creates a knowledge graph with a fixed schema of 15 relations

Tutorials Used:   
[Build a Question Answering application over a Graph Database](https://python.langchain.com/docs/tutorials/graph/)    
[Construct a Knowledge Graph with an LLM](https://python.langchain.com/docs/how_to/graph_constructing/)
