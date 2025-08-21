import os
from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()
URI = os.getenv("URI")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

# Global, reusable driver
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
