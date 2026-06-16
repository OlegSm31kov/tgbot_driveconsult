import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

class IntentClassifier:
    def __init__(self, intents_path = Path(__file__).parent.parent / 'data' / 'intents.json'):
        self.vectorizer = TfidfVectorizer(
            analyzer="char",
            ngram_range=(3, 3)
        )

        self.classifier = LinearSVC()

        self._train(intents_path)

    def _train(self, intents_path):
        with open (intents_path, 'r', encoding='utf-8') as f:
            intents = json.load(f)

        X = []
        y = []

        for intent, data in intents.items():
            for example in data["examples"]:
                X.append(example.lower())
                y.append(intent)

        X_vectorized = self.vectorizer.fit_transform(X)

        self.classifier.fit(X_vectorized, y)

    def predict(self, text):
        vector = self.vectorizer.transform([text.lower()])
        return self.classifier.predict(vector)[0]