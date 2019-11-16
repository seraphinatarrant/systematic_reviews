from enum import Enum

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


class Document(object):
    """stores information for a single document"""

    def __init__(self, source: Source, file_type: FileType, url:str="", filepath:str="", id: str=""):
        # identifiers
        self.source = source
        self.file_type = file_type
        self.url = url
        self.filepath = filepath
        self._id = id # set on upload to reference manager

        # extracted metadata
        self.reference = ""
        self.year = 0
        self.reference_identifier = ""
        self.authors = []

        # text information
        self.title = None
        self.abstract = None
        self.raw_text = ""
        self.data = {} # for data after information extraction

        assert (url or filepath), "Need to provide a source url and/or a filepath to create a Document"

    def __str__(self):
        return self.title

    def get_csv_fields(self):
        """for formatting information to write to a csv"""
        pass

    def set_reference_identifier(self):
        assert(self.reference and self.year), "Cannot create identifier without reference and year being set"
        return "{}; {}".format(self.reference, self.year)

    def add_to_collection(self, collection_id: str):
        pass


class TextField(object):
    def __init__(self, text:str, text_type: TextType):
        self.text = text
        self.text_type = text_type

    def __str__(self):
        return self.text

    def __process_text(self):
        """presumably some type of tokenization, to be built out later"""
        pass

