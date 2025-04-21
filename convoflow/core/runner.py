# convoflow/core/runner.py

from convoflow.db.metrics import SessionLogger
from convoflow.io.voice_input import transcribe_from_mic
from convoflow.io.voice_output import speak_text


class Runner:
    """
    Voice-powered IVR runner.
    Captures microphone input, uses Speack-to-Text, Zero-Shot Classification, and speaks responses aloud.
    """

    def __init__(self, graph, ai_router, start_node="start"):
        self.graph = graph
        self.ai_router = ai_router
        self.node_stack = [start_node]
        self.logger = SessionLogger()

    def run(self):
        print("\n\n\n[INTRO]")
        speak_text("Welcome to ConvoFlow. You can say 'go back' anytime.")

        while self.node_stack:
            current_node_id = self.node_stack[-1]
            current_node = self.graph.get_node(current_node_id)

            # Speak node's message
            speak_text(current_node.message)

            if not current_node.transitions:
                speak_text("This is the end of the call. Goodbye!")
                break

            user_input = transcribe_from_mic()
            print(f"You said: {user_input}")

            if "go back" in user_input.lower():
                if len(self.node_stack) > 1:
                    self.node_stack.pop()
                    continue
                else:
                    speak_text("You're already at the beginning.")
                    continue

            # Use AI Zero-Shot Classification
            options = list(current_node.transitions.keys())
            next_keyword = self.ai_router.choose_route(user_input, options)
            next_node_id = current_node.transitions.get(next_keyword)

            # Metrics
            self.logger.log_step(current_node_id, user_input, next_keyword if next_keyword else "N/A")

            if next_node_id:
                self.node_stack.append(next_node_id)
            else:
                speak_text("Sorry, I didn't understand. Let's try again.")

            print("\n")

        self.logger.end_session()