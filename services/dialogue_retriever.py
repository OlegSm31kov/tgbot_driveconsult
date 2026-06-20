import re

from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from unicodedata import normalize


class DialogueRetriever:

    def __init__(self, dialogues_path: str, similarity_threshold: float = 0.35):
        self.similarity_threshold = similarity_threshold
        self.questions = []
        self.answers = []
        self._load_dialogues(dialogues_path)
        self.vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
        self.question_vectors = (self.vectorizer.fit_transform(self.questions))

    def _load_dialogues(self, dialogues_path: str) -> None:
        path = Path(dialogues_path)
        if not path.exists():
            raise FileNotFoundError(f"Файл не найден: {dialogues_path}")

        with open(path, encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                if "|" not in line:
                    continue

                if line[-1] == "?":
                    continue

                question, answer = (
                    line.split("|", maxsplit=1)
                )

                question = question.strip()
                answer = answer.strip()

                if not question or not answer:
                    continue

                self.questions.append(normalize(question))
                self.answers.append(answer)

    def get_response(self, user_message: str ) -> str | None:
        user_message = normalize(user_message)
        user_vector = (self.vectorizer.transform([user_message]))

        similarities = cosine_similarity(user_vector, self.question_vectors)[0]
        best_index = similarities.argmax()
        best_score = similarities[best_index]

        if best_score < self.similarity_threshold:
            return None

        return self.answers[best_index]

    def get_response_with_score(self, user_message: str ) -> tuple[str | None, float]:
        user_vector = (self.vectorizer.transform([user_message]))
        similarities = cosine_similarity(user_vector, self.question_vectors)[0]
        best_index = similarities.argmax()
        best_score = similarities[best_index]

        if best_score < self.similarity_threshold:
            return None, best_score

        return self.answers[best_index], best_score

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(
        r"[^\w\s]",
        "",
        text
    )
    return " ".join(text.split())