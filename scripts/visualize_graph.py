# scripts/visualize_graph.py
import sys
import os
import logging
import codecs
import neo4j
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pyvis.network import Network
import webbrowser

# --- .env ---
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD") # No defau

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_FILENAME = "graph_visualization.html"

def fetch_graph_data(driver):
    """Fetches nodes and relationships from Neo4j."""
    nodes = []
    relationships = []
    try:
        with driver.session() as session:
            # Fetch nodes
            node_result = session.run("MATCH (n:Node) RETURN n.id AS id, n.text AS text")
            nodes = [record.data() for record in node_result]
            logger.info(f"Fetched {len(nodes)} nodes.")

            # Fetch relationships
            rel_result = session.run(
                "MATCH (source:Node)-[r:TRANSITION]->(target:Node) "
                "RETURN source.id AS source, target.id AS target, r.keyword AS keyword"
            )
            relationships = [record.data() for record in rel_result]
            logger.info(f"Fetched {len(relationships)} relationships.")

    except Exception as e:
        logger.error(f"Error fetching data from Neo4j: {e}", exc_info=True)
    return nodes, relationships

def create_visualization(nodes, relationships, filename=OUTPUT_FILENAME):
    """Creates an interactive HTML graph visualization using pyvis."""
    if not nodes:
        logger.warning("No nodes found to visualize.")
        return

    # Instantiate Network WITHOUT the heading parameter
    net = Network(height="800px", width="100%", directed=True)

    # Add nodes
    for node in nodes:
        node_id = node.get('id')
        node_text = node.get('text', '')
        if node_id:
            net.add_node(node_id, label=node_id, title=node_text)

    # Add edges (Edge label is already the keyword)
    for rel in relationships:
        source_id = rel.get('source')
        target_id = rel.get('target')
        keyword = rel.get('keyword', '')
        if source_id and target_id:
            # Remove the visible label, keep keyword for hover title
            net.add_edge(source_id, target_id, title=keyword)

    try:
        net.save_graph(filename)

        with codecs.open(filename, 'r', 'utf-8') as f:
            original_html = f.read()

        main_title = "Call Flow Graph"
        subtitle = "Hover over a node to see the text of that node"
        header_html = f"\t<h1 style=\"text-align: center;\">{main_title}</h1>\n\t<p style=\"text-align: center;\"><i>{subtitle}</i></p>\n"
        
        body_tag_pos = original_html.find("<body>")
        if body_tag_pos != -1:
            insert_pos = body_tag_pos + len("<body>")
            modified_html = original_html[:insert_pos] + "\n" + header_html + original_html[insert_pos:]
        else:
            # Fallback if <body> tag isn't found (shouldn't happen with pyvis)
            logger.warning("Could not find <body> tag; prepending header to the start.")
            modified_html = header_html + original_html
            
        with codecs.open(filename, 'w', 'utf-8') as f:
            f.write(modified_html)

        logger.info(f"Graph visualization saved to {os.path.abspath(filename)}")

        # Try to open
        try:
            webbrowser.open(f"file://{os.path.abspath(filename)}")
        except Exception as wb_err:
            logger.warning(f"Could not automatically open the HTML file: {wb_err}")
    except Exception as e:
        logger.error(f"Error saving visualization: {e}", exc_info=True)

def main():
    if not NEO4J_PASSWORD:
        logger.error("NEO4J_PASSWORD not found in environment variables or .env file.")
        sys.exit(1)

    driver = None
    try:
        logger.info(f"Attempting to connect to Neo4j at {NEO4J_URI}...")
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        driver.verify_connectivity()
        logger.info("Successfully connected to Neo4j.")

        nodes, relationships = fetch_graph_data(driver)
        create_visualization(nodes, relationships)

    except neo4j.exceptions.AuthError:
        logger.error("Neo4j authentication failed. Check credentials in .env file.")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
    finally:
        if driver:
            logger.info("Closing Neo4j connection...")
            driver.close()

if __name__ == "__main__":
    main() 