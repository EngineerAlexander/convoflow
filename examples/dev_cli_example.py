import sys
import os
from dotenv import load_dotenv
import logging # Import logging

# Add project root for imports and load environment variables
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
load_dotenv(os.path.join(project_root, '.env'))

# Configure basic logging with standard format
log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
# logger = logging.getLogger(__name__) # Optional: Get logger for this script if needed

from convoflow.core.cli_runner import CLIRunner
from convoflow.ai.ai_interface import AIRouter
from convoflow.data.graph_store import GraphStore

if __name__ == "__main__":
    try:
        graph_store = GraphStore()

        router = AIRouter()

        CLIRunner(graph_store, router).run()

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please ensure Neo4j is running, the graph is initialized (`scripts/initialize_db.py`), and .env is configured correctly.")