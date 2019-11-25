import sys
import json
import pickle
from collections import namedtuple
from enum import Enum
from typing import List, Type

from api.citoid_api import get_citation_data
from utils.general_utils import make_id, bool_partition, save_pkl, load_pkl


class TextType(Enum):
    title = 0
    abstract = 1
    body = 2
    supplementary = 3

class Source(Enum):
    journal = 0
    news = 1

class FileType(Enum):
    pdf = 0
    html = 1
    text = 3

class Label(Enum):
    exclude = 0
    include = 1

### Other Globalish things
Author = namedtuple("Author", ["firstName", "lastName", "creatorType"])

def make_authors(creators_list, text: str, split_on: str="and") -> List[dict]:
    """tries to set author from JSON, else extracts author information from raw text, returns list of dicts"""
    # Author info is of format: Hamsho, A and Tesfamarym, G and Megersa, G and Megersa, M
    if creators_list:
        return creators_list

    all_authors = []
    entries = text.split(split_on)
    for entry in entries:
        entry = entry.strip()
        try:
            last, first = entry.split(",")
        except:
            print("{} could not be split into first and last name. Entire entry will be entered in last.",
                  file=sys.stderr)
            last, first = entry.strip(), ''

        all_authors.append(Author(last, first, "author")._asdict())

    return all_authors

class Document(object):
    """stores information for a single document"""

    def __init__(self, source, file_type: FileType,
                 url: str="", filepath: str="", custom_id: int=0):
        # identifiers
        self.source = source
        self.file_type = file_type
        self.url = url
        self.filepath = filepath
        self._id = self._make_our_id(custom_id)
        self.zotero_id = None  # set on upload to reference manager
        self.issn = None
        self.doi = None

        # extracted metadata
        self.reference = ""
        self.year = 0
        self.reference_identifier = ""
        self.authors = []

        # classification
        self.gold_label = None
        self.predicted_label = None

        # text information
        self.title = None
        self.abstract = None
        self.raw_text = ""
        self.data = {} # for data after information extraction
        self.language = None

        assert (url or filepath), "Need to provide a source url and/or a filepath to create a Document"

    def __str__(self):
        return self.title

    def _make_our_id(self, custom_id):
        if custom_id:
            return custom_id
        else:
            return make_id()

    def get_id(self):
        return self._id

    def set_z_id(self, z_id: str):
        self.zotero_id = z_id

    def get_csv_fields(self):
        """for formatting information to write to a csv"""
        pass

    def set_reference_identifier(self):
        assert(self.reference and self.year), "Cannot create identifier without reference and year being set"
        return "{}; {}".format(self.reference, self.year)

    def add_to_collection(self, collection_id: str):
        pass

    def set_gold_label(self, label: Label):
        self.gold_label = label

    @classmethod
    def set_gold_labels(cls, docs, labels: List[Label]):
        for doc, label in zip(docs, labels):
            doc.gold_label = label

    def set_predicted_label(self, label: Label):
        self.predicted_label = label

    @classmethod
    def set_predicted_labels(cls, docs, labels: List[Label]):
        for doc, label in zip(docs, labels):
            doc.predicted_label = label

    @classmethod
    def filter_gold_labels(cls, docs):
        gold_labels, no_labels = bool_partition(lambda x: x.gold_label, docs)
        if len(no_labels):
            print("{} docs (out of {} total) have no gold labels and are not included...".format(
                len(list(no_labels)), len(docs)), file=sys.stderr)
            print("\n".join(map(str,no_labels)))
        return list(gold_labels)

    @classmethod
    def from_json(cls, filepath: str, batch: bool=False) -> List:
        """takes a Google Scholar JSON file, returns a Document or list of Documents"""
        with open(filepath, "r") as fin:
            data = json.load(fin)
        documents, failed = [], 0
        if batch:
            print("Processing {} docs...".format(len(data), file=sys.stderr))
            for doc in data:
                new_doc = Document.doc_from_json(doc)
                if new_doc:
                    documents.append(new_doc)
                else:
                    failed += 1
                    # TODO write failure data to log
        else:
            new_doc = Document.doc_from_json(data)
            if new_doc:
                documents = [Document.doc_from_json(data)]
            else:
                failed += 1
                # TODO write failure data to log

        return documents if len(documents) else None

    @classmethod
    def doc_from_json(cls, data: dict):
        resource_url = data["bib"]["url"]
        citation_data = get_citation_data(resource_url) # this is a dict
        if not citation_data:
            return None
        new_doc = Document(source=citation_data.get("itemType", ""),
                           file_type=FileType.pdf,
                           url=resource_url)
        new_doc.title = data["bib"]["title"]
        new_doc.year = data["bib"]["year"]
        new_doc.authors = make_authors(citation_data.get("creators", []), data["bib"]["author"])
        new_doc.doi = citation_data.get("DOI", "")
        new_doc.issn = citation_data.get("ISSN", "")
        new_doc.abstract = citation_data.get("abstractNote", "")
        new_doc.language = citation_data.get("language", "") # ISO code

        return new_doc


class TextField(object):


    def __init__(self, text:str, text_type: TextType):
        self.text = text
        self.text_type = text_type

    def __str__(self):
        return self.text

    def __process_text(self):
        """presumably some type of tokenization, to be built out later"""
        pass


if __name__ == "__main__":
    test_scraped_output = "scrapers/google_scholar/output/output.json"
    output = "output.pkl"
    new_docs = Document.from_json(test_scraped_output, batch=True)
    print(len(new_docs))
    [print(doc) for doc in new_docs]
    save_pkl(new_docs,output)
    read_docs = load_pkl(output)
    print(len(read_docs))
    [print(doc) for doc in read_docs]

