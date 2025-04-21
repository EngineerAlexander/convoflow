from convoflow.db.metrics import SessionLogger


class CLIRunner:
    """
    Command-line interface runner for IVR flows.
    Simulates user input via text, for development and testing purposes.
    Uses GraphStore to interact with a graph database (e.g., Neo4j).
    Uses SQL database to store session metrics.
    """

    def __init__(self, graph_store, ai_router, start_node="start"):
        self.graph_store = graph_store
        self.ai_router = ai_router
        self.node_stack = [start_node]
        self.logger = SessionLogger()

    def run(self):
        print("=== ConvoFlow CLI ===")
        print("Type 'go back' to return to the previous step.")
        print("Type 'exit' to quit.\n")

        while self.node_stack:
            current_node_id = self.node_stack[-1]
            current_node_text = self.graph_store.get_node_text(current_node_id)

            if current_node_text is None:
                print(f"Error: Node '{current_node_id}' not found in the database.")
                break

            neighbor_nodes = self.graph_store.get_transitions(current_node_id)
            neighbor_labels = list(neighbor_nodes.keys())

            # Current message
            print(f"[{current_node_id.upper()}]: {current_node_text}")

            if not neighbor_labels:
                print("\n[Session complete. Goodbye!]")
                break

            user_input = input("You: ").strip().lower()

            if user_input == "exit":
                break

            if user_input == "go back":
                if len(self.node_stack) > 1:
                    self.node_stack.pop()
                    continue
                else:
                    print("Already at the beginning.")
                    continue
            
            # AI Routing
            predicted_keyword = None
            predicted_keyword = self.ai_router.choose_route(user_input, neighbor_labels)

            if predicted_keyword is None:
                print(f"Router could not determine a valid transition for '{user_input}'. Please try again.")
                continue
                
            if predicted_keyword in neighbor_nodes:
                predicted_node_id = neighbor_nodes[predicted_keyword]
                self.logger.log_step(current_node_id, user_input, predicted_keyword)
                self.node_stack.append(predicted_node_id)
            else:
                 self.logger.error(f"Router returned keyword '{predicted_keyword}' which is not a valid transition from '{current_node_id}'. This indicates an internal error.")
                 print(f"Internal Error: Router selected an invalid transition. Please try again.")
                 continue
            
            print("\n")

        self.logger.end_session()