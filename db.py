import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Global, reusable driver
driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD)
)

try:
    print(URI)
    print(USER)
    print(PASSWORD)

    with driver.session() as session:
        driver.verify_connectivity()
        res = session.run("MATCH (n) RETURN n")
        print(f"result: {res.values()}")
        
except Exception as e:
    print(e)