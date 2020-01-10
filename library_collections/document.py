import logging
import sys
import json
import os
from collections import namedtuple
from enum import Enum
from typing import List, Type, Union
from dateutil import parser

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

class Publisher(Enum):
    WebOfScience = 0
    GoogleScholar = 1
    SCOPUS = 2
    MedLine = 3

### Other Globalish things
Author = namedtuple("Author", ["firstName", "lastName", "creatorType"])

def make_authors(creators_list, text: str="", split_on: str="and") -> List[dict]:
    """tries to set author from JSON, else extracts author information from raw text, returns list of dicts"""
    # Google Scholar Author info format: Hamsho, A and Tesfamarym, G and Megersa, G and Megersa, M
    # Scopus Author info format: Asmare, Kassahun;Sibhat, Berhanu;Haile, Aynalem;Sheferaw, Desie;Aragaw, Kassaye;Abera, Mesele;Abebe, Rahmeto;Wieland, Barbara"
    # TODO WoS Author info raw text parse:
    if creators_list:
        return creators_list

    all_authors = []
    entries = text.split(split_on) if text else []
    if not entries:
        return []
    for entry in entries:
        entry = entry.strip()
        try:
            last, first = entry.split(",")
        except:
            logging.warning("{} could not be split into first and last name. Entire entry will be entered in last.")
            last, first = entry.strip(), ''

        all_authors.append(Author(last, first, "author")._asdict())

    return all_authors


def get_year_from_date(date: str):
    """assume patterns are: year-mon-day or year/mon/day"""
    if not date:
        return
    date_obj = parser.parse(date)
    return date_obj.year


class Document(object):
    """stores information for a single document"""

    def __init__(self, source, file_type: FileType, url: str="", filepath: str="",
                 custom_id: int=0, zotero_id: str=None, title:str=None, abstract: str=None,
                 year:int=None, authors=None):
        # identifiers
        self.source = source
        self.file_type = file_type
        self.url = url
        self.filepath = filepath
        self._id = self._make_our_id(custom_id)
        self.zotero_id = zotero_id  # generally set on upload to reference manager
        self.issn = None
        self.doi = None

        # extracted metadata
        self.reference = ""
        self.year = year
        self.reference_identifier = ""
        self.authors = authors

        # classification
        self.gold_label = None
        self.predicted_label = None
        self.confidence = None

        # text information
        self.title = title
        self.abstract = abstract
        self.raw_text = ""
        self.data = {} # for data after information extraction
        self.language = None

        assert (url or filepath or zotero_id), "Need to provide a source url and/or a filepath to " \
                                               "create a Document if not already uploaded to Zotero"

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

    def gold_eq_predict(self) -> bool:
        if not self.gold_label or not self.predicted_label:
            logging.warning("cannot compare labels since one or both are not set")
            return False
        if self.gold_label == self.predicted_label:
            return True
        else:
            return False

    def set_gold_label(self, label: Label):
        self.gold_label = label

    @classmethod
    def set_gold_labels(cls, docs, labels: Union[List[Label] or Label], one_label=False):
        """takes docs and one label (to apply to all) or many (to zip with docs)"""
        assert not(type(labels)==List and one_label), "can either set all docs to one label or provide a list of labels, not both"
        if one_label:
            for doc in docs:
                doc.gold_label = labels
        else:
            for doc, label in zip(docs, labels):
                doc.gold_label = label

    def set_predicted_label(self, label: Label):
        if type(label) != Label:
            label = Label(label)
        self.predicted_label = label

    @classmethod
    def set_predicted_labels(cls, docs, labels: List[Label]):
        for doc, label in zip(docs, labels):
            doc.set_predicted_label(label)

    @classmethod
    def filter_gold_labels(cls, docs):
        gold_labels, no_labels = bool_partition(lambda x: x.gold_label, docs)
        if len(no_labels):
            logging.info("{} docs (out of {} total) have no gold labels and are not included...".format(
                len(list(no_labels)), len(docs)))
            logging.info("\n".join(map(str,no_labels)))
        return list(gold_labels)

    # @classmethod # Todo make it so I can cleanly pass class attributes into this method
    # def filter_fields(cls, docs, fields:List) -> List:
    #     """filter out documents where given fields are not set"""
    #     for field in fields:
    #         has_field, lacks_field = bool_partition(lambda x: x.field, docs)
    #         docs = has_field
    #         if len(lacks_field):
    #             print("Field {} is not set for {} docs (out of {} total) and will not be included."
    #                 .format(field, len(list(lacks_field)), len(docs)))
    #             print("\n".join(map(str, lacks_field)))
    #     return docs

    @classmethod
    def filter_failed_parses(cls, docs):
        # operate on the assumption that if an abstract is missing, failed to parse doc
        abstract, no_abstract = bool_partition(lambda x: x.abstract, docs)
        if len(no_abstract):
            logging.info("{} docs (out of {} total) have no abstracts and are not included...".format(
                len(list(no_abstract)), len(docs)))
            logging.info("\n".join(map(str,no_abstract)))
        return list(abstract)

    @classmethod
    def from_zotero(cls, z_doc, label=None):
        z_doc = z_doc["data"]
        # TODO make sure the zotero authors format can be handled
        new_doc = Document(Source.journal, FileType.pdf, title=z_doc.get("title"),
                           abstract=z_doc.get("abstractNote"),
                           authors=make_authors(z_doc.get("creators"), ""), zotero_id=z_doc.get("key"),
                           year=get_year_from_date(z_doc.get("date")))
        new_doc.doi = z_doc.get("DOI")
        new_doc.issn = z_doc.get("ISSN")
        if label:
            new_doc.gold_label = label
        return new_doc

    @classmethod
    def from_json(cls, filepath: str, batch: bool=False) -> List:
        """takes a JSON file, returns a Document or list of Documents"""
        source2func = {
            "Scopus" : cls.doc_from_scopus_json,
            "WoS" : cls.doc_from_wos_json,
            None: cls.doc_from_json
                       }

        with open(filepath, "r") as fin:
            data = json.load(fin)
        doc_source = data.get("metadata").get("source")
        data = data["results"] if doc_source else data # all special sources have a degree of nesting
        # skip json if no data
        if not data:
            return None

        documents, failed = [], 0
        basedir, filename = os.path.split(filepath)
        if batch:
            logging.info("Processing {} docs...".format(len(data)))
            for doc in data:
                new_doc = source2func[doc_source](doc, basedir=basedir)
                if new_doc:
                    documents.append(new_doc)
                else:
                    failed += 1
                    logging.debug("Failed to create doc from data: {}".format(doc))
        else:
            assert type(data) != list, "Tried to create a single doc but received a list. " \
                                       "Did you mean to set batch=True?"
            new_doc = source2func[doc_source](data, basedir=basedir)
            if new_doc:
                documents = [new_doc]
            else:
                logging.debug("Failed to create doc from data: {}".format(data))
        logging.info("{} documents failed to retrieve metadata and were skipped, "
              "out of {} total ({:2f}) %".format(failed, len(data), (failed/len(data))*100))
        return documents if documents else None

    # TODO refactor all of these so there isn't duplicative code
    @classmethod
    def doc_from_json(cls, data: dict, basedir: str):
        """default creates a doc from json - based on Google Scholar format"""
        resource_url = data["bib"]["url"]
        citation_data = get_citation_data(resource_url) # this is a dict

        filename = data.get("saved_pdf_name", "")
        if not citation_data:
            logging.debug("Failed - URL: {} PDF: {}".format(resource_url,filename))
            return None
        filepath = os.path.join(basedir, filename) if filename else ""

        new_doc = Document(source=citation_data.get("itemType", ""),
                           file_type=FileType.pdf,
                           url=resource_url, filepath=filepath)
        title = data["bib"].get("title")
        year = data["bib"].get("year")
        new_doc.title = title if title else citation_data.get("title")
        new_doc.year = int(year) if year else get_year_from_date(citation_data.get("date"))
        new_doc.authors = make_authors(citation_data.get("creators", []), data["bib"]["author"])
        new_doc.set_info_from_citation(citation_data)

        return new_doc

    @classmethod
    def doc_from_wos_json(cls, data: dict, basedir: str):
        filename = data.get("saved_pdf_name", "")
        doi = data.get("Identifier.Doi")
        if not doi:
            logging.debug("Couldn't find a DOI for PDF: {}, skipping".format(filename))
            return None
        filename = doi + ".pdf" # TODO change this when format fixed
        citation_data = get_citation_data(doi)  # this is a dict
        if not citation_data:
            logging.debug("Failed - PDF: {}".format(filename))
            return None
        filepath = os.path.join(basedir, filename) if filename else ""

        new_doc = Document(source=citation_data.get("itemType", ""),
                           file_type=FileType.pdf, filepath=filepath)
        # populate fields
        title = data.get("title")
        new_doc.title = title if title else citation_data.get("title")
        new_doc.authors = make_authors(citation_data.get("creators", []), data["authors"],
                                       split_on=";")
        new_doc.set_info_from_citation(citation_data)

    @classmethod
    def doc_from_scopus_json(cls, data: dict, basedir: str):
        filename = data.get("saved_pdf_name", "")
        doi = data.get("doi")
        if not doi:
            logging.debug("Couldn't find a DOI for PDF: {}, skipping".format(filename))
            return None
        filename = doi + ".pdf"  # TODO fix this later
        citation_data = get_citation_data(doi)  # this is a dict
        if not citation_data:
            logging.debug("Failed - PDF: {}".format(filename))
            return None
        filepath = os.path.join(basedir, filename) if filename else ""

        new_doc = Document(source=citation_data.get("itemType", ""),
                           file_type=FileType.pdf, filepath=filepath)
        # populate fields
        new_doc.title = data.get("title")
        new_doc.abstract = data.get("description")
        new_doc.authors = make_authors(citation_data.get("creators", []), data["author_names"],
                                       split_on=";")
        new_doc.set_info_from_citation(citation_data)

        return new_doc

    def set_info_from_citation(self, citation_data):
        self.title = citation_data.get("title", "") if not self.title else self.title
        self.abstract = citation_data.get("abstractNote", "") if not self.abstract else self.abstract
        self.doi = citation_data.get("DOI", "")
        self.issn = citation_data.get("ISSN", "")
        self.language = citation_data.get("language", "")  # ISO code


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

