import sys
from abc import ABCMeta, abstractmethod
from typing import TypeVar, Type, List, Dict

from library_collections.document import Document

T = TypeVar("T", bound="ClassificationStrategy")


class Classifier(metaclass=ABCMeta):
    """An Abstract Classifier class, designed to take Documents as input and output labels"""

    __name_to_strategy = dict()
    CONFIG_STRATEGY_NAME_KEY = "name"
    label2idx = None # set by config
    idx2label = None

    @property
    @abstractmethod
    def name(cls):
        """Name of the classification strategy"""

    @classmethod
    def register_strategy(cls, scls):
        """Adds the subclasses to the mapping where the key is `Classifier.name` and the
        value is the class.

        :param scls: the subclass to register
        :return: the subclass
        """
        cls.__name_to_strategy[scls.name] = scls
        return scls

    @classmethod
    def from_config(cls: Type[T], config: Dict) -> T:
        """Reads the classification strategy from a dictionary, performs validation"""

        # Get the name of the strategy to be used for classification from the strategy configuration.
        strategy_name = config.get(Classifier.CONFIG_STRATEGY_NAME_KEY)
        if strategy_name is None:
            raise ValueError("No strategy config entry for '{0}'".format(Classifier.CONFIG_STRATEGY_NAME_KEY))

        # Get the class name of the strategy to be used, raise an exception if the strategy name is unknown.
        strategy = Classifier.__name_to_strategy.get(strategy_name.lower())
        if strategy is None:
            raise ValueError("No strategy name '{0}'".format(strategy_name))

        # Create the strategy instance from the strategy config.
        return strategy.from_strategy_config(config)

    @classmethod
    @abstractmethod
    def from_strategy_config(cls, config: Dict):
        pass

    @abstractmethod
    def classify_documents(self, items: List[Document]) -> List[int]:
        pass

    @abstractmethod
    def classify_raw_data(self, items: List[str]) -> List[int]:
        pass

    def classify(self, items:List) -> List[int]:
        """router for classification strategy: takes a list of objects and returns a list of
        integers corresponding to labels"""
        first_object = items[0]
        if type(first_object) == Document:
            return self.classify_documents(items)
        else: # assume raw text
            print("Classifying (probably) raw input. First sample:\n {}".format(first_object), file=sys.stderr)
            return self.classify_raw_data(items)