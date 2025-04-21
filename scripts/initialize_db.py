import sys
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Add the project root for GraphStore import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
try:
    from convoflow.data.graph_store import GraphStore
except ImportError as e:
    print(f"Error importing GraphStore: {e}")
    print("Make sure the script is run from the project root or the path is correctly set.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    store = None
    try:
        logger.info("Attempting to connect to Neo4j...")
        # Assumes NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD environment variables are set
        # or defaults (bolt://localhost:7687, neo4j, password) are correct
        store = GraphStore()
        logger.info("Successfully connected to Neo4j.")

        logger.info("Clearing existing graph data...")
        store.clear_graph()
        logger.info("Graph data cleared.")

        logger.info("Adding nodes and relationships...")
        
        # CREATE YOUR GRAPH HERE (BE ADVISED THAT SPECIFIC NAMING IS RECOMMENDED FOR BETTER AI ROUTING)
        store.add_node("start", "I'm CoolCompany's assistant. What can I help you with today? I can help you with billing, customer support, and business hours.", {
            "billing": "billing",
            "customer_support": "customer_support",
            "business_hours": "business_hours"
        })
        
        store.add_node("billing", "Want to check your balance or make a payment?", {
            "account_balance": "account_balance",
            "make_payment": "make_payment"
        })
        
        store.add_node("account_balance", "Redirecting to balance system...")
        
        store.add_node("make_payment", "Redirecting to payment system...")
        
        store.add_node("customer_support", "Would you like to speak to a customer service representative or inquire about an order?", {
            "speak_to_representative": "speak_to_representative",
            "inquire_about_order": "inquire_about_order"
        })
        
        store.add_node("speak_to_representative", "Redirecting to customer service representative...")
        
        store.add_node("inquire_about_order", "Redirecting to order tracking system...")
        
        store.add_node("business_hours", "We are open 9am–5pm Monday through Friday, 10am–2pm Saturday.")

        # END OF CREATE YOUR GRAPH

        logger.info("Successfully initialized the Neo4j database with the call graph.")

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f"An error occurred during database initialization: {e}", exc_info=True)
    finally:
        if store:
            logger.info("Closing Neo4j connection...")
            store.close()

if __name__ == "__main__":
    main() 