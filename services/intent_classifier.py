from pathlib import Path

import joblib

from services.text_preprocessor import preprocess


class IntentClassifier:

    def __init__(self):

        model_dir = Path(__file__).parent.parent / "models"

        self.classifier = joblib.load(
            model_dir / "intent_model.pkl"
        )

        self.vectorizer = joblib.load(
            model_dir / "vectorizer.pkl"
        )

    def predict(self, text):
        normalized = preprocess(text)

        vector = self.vectorizer.transform([normalized])
        scores = self.classifier.decision_function(vector)[0]
        best_idx = scores.argmax()

        return self.classifier.classes_[best_idx], float(scores[best_idx])