from typing import List, Type
from .document import Document, Label

class Collection(object):
    """a collection of Documents, mimics the organisation of a reference manager"""
    def __init__(self, name: str, _id=None, parent: str=None, documents: List[Document]=None):
        self.name = name
        self._id = _id
        self.parent = parent
        self.documents = documents

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
        if self.name == "include":
            return Label.include
        elif self.name == "exclude":
            return Label.exclude
        else:
            pass

    @classmethod
    def from_zotero(cls, z_library) -> List:
        """takes a Zotero library after auth and returns a list of all the collections"""
        z_collections = z_library.collections()
        # TODO make sure capture parents if exist
        all_collections = [Collection(col["data"]["name"], col["key"], documents=[])
                           for col in z_collections]
        for col in all_collections:
            # have to wrap in zotero.everything() else API only returns 100 items
            collection_docs = z_library.everything(z_library.collection_items_top(col.get_id())) # this returns a list of dicts corresponding to articles
            collection_label = col.find_collection_label()
            for z_doc in collection_docs:
                new_doc = Document.from_zotero(z_doc, collection_label)
                col.add_document(new_doc)
        return all_collections




