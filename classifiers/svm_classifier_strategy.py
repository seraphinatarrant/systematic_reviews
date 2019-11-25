import pickle
import sys
from typing import Dict, List, Tuple

import numpy as np
from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

from .classifier_strategy import ClassifierStrategy
from library_collections.document import Document, Label
from utils.general_utils import save_pkl


def format_data(items: List[Document], has_labels=True) -> Tuple[List[str], List[int]]:
    """unpacks documents into Lists of strings and labels (if present). Test data will have has_labels = False"""
    text_data, label_data = [], []
    for item in items:
        text_data.append(item.title + item.abstract)  # simple concat of title and abstract for now
        if has_labels:
            label_data.append(item.gold_label.value)

    return text_data, label_data

def print_prediction_accuracy(predictions: List[int], gold_labels: List[int]):
    accuracy = np.mean(predictions == gold_labels)
    print("Classifier Accuracy: {}".format(accuracy))
    print("-" * 89)
    print("Classification Report:")
    print(metrics.classification_report(gold_labels, predictions,
                                        target_names=[l.name for l in Label]))
    print(metrics.confusion_matrix(gold_labels, predictions, labels=[l.name for l in Label]))

@ClassifierStrategy.register_strategy
class SVMClassifier(ClassifierStrategy):

    def __init__(self, vectorizer, classifier, path=""):
        self.vectorizer = vectorizer
        self.classifier = classifier
        self.path = path
        self.pipeline = None # this will be set once trained

    name = "svm"

    VECTOR_TYPE_KEY = "vector_type"
    # TODO add other config options

    @classmethod
    def from_strategy_config(cls, config: Dict):
        pretrained_model = config["model"].get("pretrained", False)
        if pretrained_model:
            with open(pretrained_model, "rb") as fin:
                return pickle.load(fin)
        else:
            model_name = config["model"].get("path","model.pt")
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

            return cls(vectorizer, classifier, path=model_name)

    def train_classifier(self, train_items: List[Document], test_items: List[Document]=None):
        # make training data
        text_data, text_labels = format_data(train_items)
        # make pipeline
        classifier_pipeline = Pipeline([
            ("vectors", self.vectorizer),
            ("classifier", self.classifier)
        ])
        # classify
        classifier_pipeline.fit(text_data, text_labels)
        self.pipeline = classifier_pipeline
        print("Saving classifier to {}".format(self.path), file=sys.stderr)
        save_pkl(self, self.path)
        # print out test accuracy if exists
        # TODO make this logged
        if test_items:
            self.classify_documents(test_items, has_labels=True)

    def classify_documents(self, items: List[Document], has_labels=False) -> List[Label]:
        """classifies documents. If has labels, will also print accuracy"""
        # make training data -> should work if gold labels are not set, that should be a boolean in the function
        texts, labels = format_data(items, has_labels)
        # classify
        assert self.pipeline, "Pipeline does not exist, classifier needs to be trained with .train_classifier()"
        predictions = self.pipeline.predict(texts)
        if has_labels:
            print_prediction_accuracy(predictions, labels)
        # set predicted label attributes on documents
        Document.set_predicted_labels(items, predictions)
        # return list of labels
        return predictions

    def classify_raw_data(self, items: List[str]) -> List[int]:
        pass
