import yaml
import sys
from typing import Dict, List, Tuple

import numpy as np
from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

from .classifier_strategy import ClassifierStrategy
from library_collections.document import Document, Label


def make_training_data(self, items: List[Document]) -> Tuple[List[str], List[int]]:
    """unpacks documents into Lists of strings and labels"""
    text_data, label_data = [], []
    for item in items:
        text_data.append(item.title + item.abstract)  # simple concat of title and abstract for now
        label_data.append(item.gold_label.value)

    return text_data, label_data

@ClassifierStrategy.register_strategy
class SVMClassifier(ClassifierStrategy):

    def __init__(self, vectorizer, classifier):
        self.vectorizer = vectorizer
        self.classifier = classifier
        self.pipeline = None

    name = "svm"
    VECTOR_TYPE_KEY = "vector_type"
    # TODO add other config options

    @classmethod
    def from_strategy_config(cls, config: Dict):
        # Vectors
        vector_type = config.get(SVMClassifier.VECTOR_TYPE_KEY, "tf-idf")
        if vector_type == "tf-idf":
            vectorizer = TfidfVectorizer()
        elif vector_type == "bow":
            vectorizer = CountVectorizer()
        else:
            sys.exit("unsupported vector type {}".format(vector_type))
        # Classifier params
        # TODO add whatever needs to be changeable to the config
        classifier = SGDClassifier(max_iter=5) # This is just dummy

        return cls(vectorizer, classifier)

    def train_classifier(self, train_items: List[Document], test_items: List[Document]=None):
        # make training data
        text_data, text_labels = make_training_data(train_items)
        # make pipeline
        classifier_pipeline = Pipeline([
            ("vectors", self.vectorizer),
            ("classifier", self.classifier)
        ])
        # classify
        classifier_pipeline.fit(text_data, text_labels)
        self.pipeline = classifier_pipeline
        # print out test accuracy if exists
        # TODO make this logged
        if test_items:
            self.print_prediction_accuracy(test_items)

    def print_prediction_accuracy(self, items: List[Document]):
        test_data, test_labels = make_training_data(items)
        predictions = self.pipeline.predict(test_data)
        accuracy = np.mean(predictions == test_labels)
        print("Classifier Accuracy: {}".format(accuracy))
        print("-" * 89)
        print("Classification Report:")
        print(metrics.classification_report(test_labels, predictions,
                                            target_names=[l.name for l in Label]))
        print(metrics.confusion_matrix(test_labels, predictions, labels=[l.name for l in Label]))

    def classify_documents(self, items: List[Document]) -> List[Label]:
        # make training data -> should work if gold labels are not set, that should be a boolean in the function
        # classify
        # set predicted label attributes on documents
        # return list of labels
        pass

    def classify_raw_data(self, items: List[str]) -> List[int]:
        pass
