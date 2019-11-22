from typing import List, Type
from .document import Document

class Collection(object):
    """a collection of Documents, mimics the organisation of a reference manager"""
    def __init__(self, name: str, id=None, parent: str=None, documents: List[Document]=None):
        self.name = name
        self._id = id
        self.parent = parent
        self.documents = documents

    def __str__(self):
        return self.name

    def set_id(self): #used to set ID for whatever type of reference manager is being used
        pass

    def add_documents(self, docs: List[Document]):
        self.documents.extend(docs)
