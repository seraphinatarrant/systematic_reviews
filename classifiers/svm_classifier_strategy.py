import pickle
import sys
from typing import Dict, List, Tuple
import logging
from datetime import datetime

import numpy as np
import os
from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt

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

def print_prediction_accuracy(predictions: List[int], gold_labels: List[int], conf_thresh=False):
    accuracy = np.mean(predictions == gold_labels)
    matrix_labels = [l.name for l in Label]+[] if not conf_thresh else [l.name for l in Label]+["below thresh"]
    logging.info("Classifier Accuracy: {}".format(accuracy))
    logging.info("-" * 89)
    logging.info("Classification Report:")
    logging.info(metrics.classification_report(gold_labels, predictions,
                                        target_names=matrix_labels))
    logging.info("Confusion Matrix:")
    logging.info(metrics.confusion_matrix(gold_labels, predictions, labels=[l.value for l in Label]))


def convert_confidences_to_labels(predictions, threshold) -> List:
    """takes a set of scores and converts them to binary labels depending on a threshold"""
    labels, num_below_thresh = [], 0
    for p in predictions:
        if abs(p) < threshold:
            labels.append(-1)
            num_below_thresh += 1
            continue
        label = 1 if p > 0 else 0
        labels.append(label)
    logging.info("{}/{} documents were below the confidence threshold of {}".format(
        num_below_thresh,
        len(predictions),
        threshold))
    return labels


@ClassifierStrategy.register_strategy
class SVMClassifier(ClassifierStrategy):

    def __init__(self, vectorizer, classifier, path=""):
        self.vectorizer = vectorizer
        self.classifier = classifier
        self.path = path
        self.pipeline = None # this will be set once trained

    name = "svm"
    PRETRAINED_KEY = "pretrained"
    SAVE_LOC_KEY = "save_loc"

    VECTOR_TYPE_KEY = "vector_type"
    LOSS_KEY = "loss"
    REG_KEY = "regularizer"
    LR_KEY = "lr"
    STOP_KEY = "early_stopping"
    BALANCE_KEY = "balance_classes"
    MAX_ITER_KEY = "max_iter"

    @classmethod
    def from_strategy_config(cls, config: Dict):
        pretrained_model = config["model"].get(SVMClassifier.PRETRAINED_KEY, False)
        if pretrained_model:
            with open(pretrained_model, "rb") as fin:
                return pickle.load(fin)
        else:
            model_name = config["model"].get(SVMClassifier.SAVE_LOC_KEY,"model.pt")
            param_config = config["strategy"]
            # Vector types
            vector_type = param_config.get(SVMClassifier.VECTOR_TYPE_KEY, "tf-idf")
            if vector_type == "tf-idf":
                vectorizer = TfidfVectorizer()
            elif vector_type == "bow":
                vectorizer = CountVectorizer()
            else:
                sys.exit("unsupported vector type {}".format(vector_type))
            # Classifier params, including defaults
            class_weight = "balanced" if param_config.get(SVMClassifier.BALANCE_KEY) else None
            classifier = SGDClassifier(loss=param_config.get(SVMClassifier.LOSS_KEY, "hinge"),
                                       penalty=param_config.get(SVMClassifier.REG_KEY, "l2"),
                                       learning_rate=param_config.get(SVMClassifier.LR_KEY, "optimal"),
                                       early_stopping=param_config.get(SVMClassifier.STOP_KEY, True),
                                       class_weight=class_weight,
                                       max_iter=param_config.get(SVMClassifier.MAX_ITER_KEY, 1000)
                                       )

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
        logging.info("Training classifier with params:")
        logging.info(self.classifier.get_params())
        classifier_pipeline.fit(text_data, text_labels)
        self.pipeline = classifier_pipeline
        logging.info("Saving classifier to {}".format(self.path))
        save_pkl(self, self.path)
        # visualise features
        self.plot_coefficients()
        # print out test accuracy if exists
        if test_items:
            self.classify_documents(test_items, has_labels=True)

    def classify_documents(self, items: List[Document], has_labels=False,
                           confidence=False, threshold: float=None):
        """classifies documents. If has labels, will also print accuracy. Returns a numpy array of label integers"""
        # make training data -> should work if gold labels are not set, that should be a boolean in the function
        texts, labels = format_data(items, has_labels)
        # classify
        assert self.pipeline, "Pipeline does not exist, classifier needs to be trained with .train_classifier()"
        if confidence:
            # Signed distance of that sample to the decision boundary
            # returns confidence where < 0 is label 0 and > 0 is label 1.
            predictions = self.pipeline.decision_function(texts)
            predictions = convert_confidences_to_labels(predictions, threshold)
        else:
            predictions = self.pipeline.predict(texts)
        if has_labels:
            print_prediction_accuracy(predictions, labels, conf_thresh=confidence)
        # set predicted label attributes on documents
        Document.set_predicted_labels(items, predictions)
        # return list of labels
        return predictions

    def classify_raw_data(self, items: List[str]) -> List[int]:
        pass


    def plot_coefficients(self, top_features=50):
        plot_name = os.path.join(
            os.path.dirname(logging.getLogger().handlers[0].baseFilename),
            self.path +": " + str(datetime.now()) + ".png")
        coef = self.classifier.coef_.ravel()
        feature_names = self.vectorizer.get_feature_names()
        top_positive_coefficients = np.argsort(coef)[-top_features:]
        top_negative_coefficients = np.argsort(coef)[:top_features]
        top_coefficients = np.hstack([top_negative_coefficients, top_positive_coefficients])
        # create plot
        plt.figure(figsize=(15, 5))
        colors = ["red" if c < 0 else "blue" for c in coef[top_coefficients]]
        plt.bar(np.arange(2 * top_features), coef[top_coefficients], color=colors)
        feature_names = np.array(feature_names)
        plt.xticks(np.arange(1, 1 + 2 * top_features), feature_names[top_coefficients], rotation=60,
                   ha="right")
        plt.tick_params(axis="x", which="major", pad=3, labelsize=8) # Note that labelsize 8pt is set for 50 features. (so it all fits without overlapping)

        logging.info("Saving feature plot to {}".format(plot_name))
        plt.savefig(plot_name, bbox_inches="tight")