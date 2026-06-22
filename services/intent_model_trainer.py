import json
from pathlib import Path
import joblib

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)
from sklearn.model_selection import learning_curve
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC

from services.text_preprocessor import preprocess


INTENTS_PATH = Path(__file__).parent.parent / "data" / "intents.json"
MODELS_DIR = Path(__file__).parent.parent / "models"

MODELS_DIR.mkdir(exist_ok=True)


with open(INTENTS_PATH, "r", encoding="utf-8") as f:
    intents = json.load(f)

X = []
y = []

for intent, data in intents.items():
    for example in data["examples"]:
        X.append(preprocess(example))
        y.append(intent)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3, 3)
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

classifier = LinearSVC()

classifier.fit(X_train_vec, y_train)

predictions = classifier.predict(X_test_vec)

accuracy = accuracy_score(y_test, predictions)

print(f"\nAccuracy: {accuracy:.4f}\n")

print(
    classification_report(
        y_test,
        predictions,
        digits=4
    )
)

joblib.dump(classifier, MODELS_DIR / "intent_model.pkl")
joblib.dump(vectorizer, MODELS_DIR / "vectorizer.pkl")

print("\nМодель сохранена\n")

# Матрица ошибок
labels = sorted(set(y))

cm = confusion_matrix(
    y_test,
    predictions,
    labels=labels
)

plt.figure(figsize=(10, 8))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    xticklabels=labels,
    yticklabels=labels
)

plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("True")
plt.tight_layout()

plt.savefig(Path(__file__).parent.parent / "models" / "LinearSVC_confusion_matrix.png")
plt.show()

# Learning curve
train_sizes, train_scores, test_scores = learning_curve(
    estimator=classifier,
    X=vectorizer.transform(X),
    y=y,
    cv=5,
    scoring="accuracy",
    train_sizes=np.linspace(0.1, 1.0, 10),
    n_jobs=-1
)

train_mean = train_scores.mean(axis=1)
test_mean = test_scores.mean(axis=1)

plt.figure(figsize=(8, 5))

plt.plot(
    train_sizes,
    train_mean,
    marker="o",
    label="Train accuracy"
)

plt.plot(
    train_sizes,
    test_mean,
    marker="o",
    label="Validation accuracy"
)

plt.xlabel("Training examples")
plt.ylabel("Accuracy")
plt.title("Learning Curve")
plt.legend()
plt.grid(True)

plt.savefig(Path(__file__).parent.parent / "models" / "LinearSVC_learning_curve.png")
plt.show()