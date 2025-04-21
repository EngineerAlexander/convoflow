from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class AIRouter:
    def __init__(self, model_name="facebook/bart-large-mnli"):
        self.classifier = pipeline("zero-shot-classification", model=model_name)

    def choose_route(self, user_input, candidate_labels: list[str]):
        """Classifies user input against candidate labels."""
        if not candidate_labels:
            logger.warning(f"Choose route called with no candidate labels for input: '{user_input}'")
            return None

        if len(candidate_labels) == 1:
            return candidate_labels[0]

        # Run zero-shot classification
        results = self.classifier(user_input, candidate_labels)

        if not results or not results['labels']:
            logger.warning(f"Classifier returned no results for input '{user_input}' with candidates: {candidate_labels}")
            return None
            
        best_label = results['labels'][0]
        best_score = results['scores'][0]

        # Log all scores for debugging
        all_scores_str = ", ".join([f"'{l}': {s:.4f}" for l, s in zip(results['labels'], results['scores'])])
        logger.info(f"Best: '{best_label}' ({best_score:.4f}) | All scores: {{{all_scores_str}}}")

        return best_label