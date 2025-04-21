# examples/example.py (Voice Input CLI)
import sys
import os
import logging
from dotenv import load_dotenv

# Add project root and load environment variables
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
load_dotenv(os.path.join(project_root, '.env'))

# Configure basic logging with standard format
log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__) # Get logger for this script specifically if needed

# Import necessary components
from convoflow.data.graph_store import GraphStore
from convoflow.ai.ai_interface import AIRouter
from convoflow.db.metrics import SessionLogger
from convoflow.io.voice_input import transcribe_from_mic
from convoflow.io.voice_output import speak_text

def run_voice_cli(graph_store, ai_router, start_node="start"):
    """Runs a CLI-like loop using transcribed voice input and TTS output."""
    node_stack = [start_node]
    logger = SessionLogger()

    print("=== ConvoFlow Voice CLI ===")
    speak_text("Welcome to the ConvoFlow voice assistant.\nSay 'go back' to return to the previous step.\nSay 'exit' to quit.")

    while node_stack:
        current_node_id = node_stack[-1]
        current_node_text = graph_store.get_node_text(current_node_id)

        if current_node_text is None:
            error_msg = f"Error: Node '{current_node_id}' not found in the database."
            print(error_msg)
            break

        neighbor_nodes = graph_store.get_transitions(current_node_id)
        neighbor_labels = list(neighbor_nodes.keys())

        # Display and speak current node message
        print(f"[{current_node_id.upper()}]")
        try:
            speak_text(current_node_text)
        except Exception as e:
            logger.error(f"TTS Error (Node: {current_node_id}): {e}", exc_info=True)
            print("(TTS Error occurred)")

        # Check if terminal node          
        if not neighbor_labels:
            break

        # Listen and transcribe
        try:
            user_input = transcribe_from_mic()
            if user_input:
                print(f"You said (transcribed): {user_input}")
            else:
                print("(No speech detected or transcription failed, please try again.)")
                continue # Ask again at the same node
        except Exception as e:
            logger.error(f"Error during transcription: {e}", exc_info=True)
            print("Sorry, there was an error getting your input. Please try again.")
            continue
        
        if user_input == "exit":
            break

        if user_input == "back":
            if len(node_stack) > 1:
                node_stack.pop()
                continue
            else:
                print("Already at the beginning.")
                continue
        
        # AI Routing
        predicted_keyword = ai_router.choose_route(user_input, neighbor_labels)

        if predicted_keyword is None:
            print(f"Router could not determine a valid transition for what you said. Please try again.")
            continue
            
        if predicted_keyword in neighbor_nodes:
            predicted_node_id = neighbor_nodes[predicted_keyword]
            logger.log_step(current_node_id, user_input, predicted_keyword)
            node_stack.append(predicted_node_id)
        else:
             logger.error(f"Router returned keyword '{predicted_keyword}' which is not a valid transition from '{current_node_id}'. This indicates an internal error.")
             print(f"Internal Error: Router selected an invalid transition. Please try again.")
             continue

    goodbye_message = "Session complete. Goodbye!"
    print(f"\n[{goodbye_message}]")
    try:
        speak_text(goodbye_message)
    except Exception as e:
        logger.error(f"TTS Error (Goodbye): {e}", exc_info=True)
        print("(TTS Error occurred)")

if __name__ == "__main__":
    try:
        graph_store = GraphStore()

        ai_router = AIRouter()

        run_voice_cli(graph_store, ai_router)

    except ImportError as e:
        logger.error(f"Import error: {e}. Ensure all dependencies are installed, especially for voice input.")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        print(f"\nAn error occurred: {e}")
        print("Please ensure Neo4j is running, the graph is initialized (`scripts/initialize_db.py`), and .env is configured correctly.")
