import pickle
from typing import List
from library_collections.document import Document
from utils.general_utils import load_pkl, save_pkl



class Corpus(object):

    def __init__(self, train_docs: List[Document]=None, test_docs: List[Document]=None):
        self.train = train_docs
        self.test = test_docs

    @classmethod
    def from_config(cls, config):
        train, test = config["corpus"].get("train"), config["corpus"].get("test")
        new_corpus = cls()
        if train:
            new_corpus.train = load_pkl(train)
        if test:
            new_corpus.test = load_pkl(test)

        return new_corpus

    def save(self, path):
        save_pkl(self, path)
