import os
from neo4j import GraphDatabase
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GraphStore:
    def __init__(self, uri=None, user=None, password=None):
        # Use environment variables or defaults
        uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = user or os.getenv("NEO4J_USERNAME", "neo4j")
        _password_to_use = password or os.getenv("NEO4J_PASSWORD", "password")

        if not uri or not user or not _password_to_use:
            raise ValueError("Neo4j connection details...")

        try:
            self._driver = GraphDatabase.driver(uri, auth=(user, _password_to_use))
            self._driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j at {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed.")

    def _execute_write_query(self, query, parameters=None):
        try:
            with self._driver.session() as session:
                result = session.execute_write(lambda tx: tx.run(query, parameters).data())
                return result
        except Exception as e:
            logger.error(f"Error executing write query: {query} | Params: {parameters} | Error: {e}")
            raise

    def _execute_read_query(self, query, parameters=None):
        try:
            with self._driver.session() as session:
                result = session.execute_read(lambda tx: tx.run(query, parameters).data())
                return result
        except Exception as e:
            logger.error(f"Error executing read query: {query} | Params: {parameters} | Error: {e}")
            raise

    def get_node_text(self, node_id):
        """Retrieves the text property of a specific node."""
        query = "MATCH (n:Node {id: $node_id}) RETURN n.text AS text"
        result = self._execute_read_query(query, {'node_id': node_id})
        if result:
            return result[0].get('text')
        logger.warning(f"Node with id '{node_id}' not found.")
        return None

    def get_transitions(self, node_id):
        """Retrieves the outgoing transitions for a specific node."""
        query = (
            "MATCH (source:Node {id: $node_id})-[r:TRANSITION]->(target:Node) "
            "RETURN r.keyword AS keyword, target.id AS target_id"
        )
        results = self._execute_read_query(query, {'node_id': node_id})
        transitions = {res['keyword']: res['target_id'] for res in results}
        logger.debug(f"Transitions for node '{node_id}': {transitions}")
        return transitions

    def add_node(self, node_id, text, options=None):
        # Create or update the node with its properties
        query = (
            "MERGE (n:Node {id: $node_id}) "
            "SET n.text = $text "
            "RETURN n"
        )
        try:
            self._execute_write_query(query, {'node_id': node_id, 'text': text})
            logger.debug(f"Added/updated node: {node_id}")
        except Exception as e:
            raise

        if options:
            for keyword, target_node_id in options.items():
                self.add_relationship(node_id, target_node_id, keyword)

    def add_relationship(self, source_node_id, target_node_id, keyword):
        # Ensure target node exists (or create a placeholder if necessary, though ideally targets are added first)
        # Using MERGE ensures we don't create duplicate relationships for the same keyword
        query = (
            "MERGE (source:Node {id: $source_id}) "
            "MERGE (target:Node {id: $target_id}) "
            "MERGE (source)-[r:TRANSITION {keyword: $keyword}]->(target) "
            "RETURN r"
        )
        self._execute_write_query(query, {
            'source_id': source_node_id,
            'target_id': target_node_id,
            'keyword': keyword
        })
        logger.debug(f"Added relationship: ({source_node_id}) -[{keyword}]-> ({target_node_id})")

    def clear_graph(self):
        query = "MATCH (n) DETACH DELETE n"
        try:
            self._execute_write_query(query)
            logger.info("Cleared all nodes and relationships from the graph.")
        except Exception as e:
            raise