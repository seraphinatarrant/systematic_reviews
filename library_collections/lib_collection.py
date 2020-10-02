from typing import List, Type
from api.zotero_api import get_collection_names_and_IDs
from .document import Document, Label

class Collection(object):
    """a collection of Documents, mimics the organisation of a reference manager"""
    def __init__(self, name: str, _id=None, parent: str=None, documents: List[Document]=None):
        self.name = name
        self._id = _id
        self.parent = parent
        self.documents = documents
        # for some experiments with very specific test-train splits
        self.train_docs = None
        self.test_docs = None

    def __str__(self):
        return self.name

    def set_id(self): #used to set ID for whatever type of reference manager is being used
        pass

    def get_id(self):
        return self._id

    def add_documents(self, docs: List[Document]):
        self.documents.extend(docs)

    def add_document(self, doc: Document):
        self.documents.append(doc)

    def find_collection_label(self) -> Label:
        if "include" in self.name:
            return Label.include
        elif "exclude" in self.name:
            return Label.exclude
        else:
            pass

    @classmethod
    def from_zotero(cls, z_library, include_only=None) -> List:
        """takes a Zotero library after auth and returns a list of all the collections"""
        z_collections = z_library.collections()
        # get names including parent names
        name2id = get_collection_names_and_IDs(z_collections, z_library)

        if include_only:  # filter out things without a region string for experiment conditions
            for name in list(name2id.keys()):
                include = False
                for text in include_only:
                    if text in name.lower():
                        include = True
                if not include:
                    del name2id[name]
            print("modified dict {}".format(name2id.keys()))

        all_collections = [Collection(col, name2id[col], documents=[])
                           for col in name2id]
        for col in all_collections:
            # have to wrap in zotero.everything() else API only returns 100 items
            collection_docs = z_library.everything(z_library.collection_items_top(col.get_id())) # this returns a list of dicts corresponding to articles
            collection_label = col.find_collection_label()
            for z_doc in collection_docs:
                new_doc = Document.from_zotero(z_doc, collection_label)
                col.add_document(new_doc)
        return all_collections




