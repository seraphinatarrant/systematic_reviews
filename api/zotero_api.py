import argparse
import sys
from typing import List, Type, Dict
from enum import Enum

from pyzotero import zotero

from library_collections.document import Document
from utils.general_utils import read_yaml_config


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-c', dest='config_file', default='../config/zotero.yaml',
                   help='a yaml config containing necessary API information')
    return p.parse_args()

def auth_zotero_library(config: Dict):
    """returns a zotero library object"""
    auth = config["auth"]
    return zotero.Zotero(auth["library_id"], auth["library_type"], auth["api_key"])

### Collections
def get_all_collections(z_library) -> List[Dict]:
    return z_library.collections()

def get_collection_IDs(collections: List[Dict]) -> List[str]:
    return [col["key"] for col in collections]

def get_collection_names_and_IDs(collections: List[Dict], z_library) -> Dict:
    name2id = {}
    for col in collections:
        name = col["data"]["name"]
        parent = col["data"]["parentCollection"]
        if parent:
            # prepend parent name. Assume only one degree of nesting
            parent_name = z_library.collection(parent)["data"]["name"]
            name = parent_name + "_" + name
        name2id[name] = col["key"]
    return name2id

def create_collections(z_library, names:List[str]):
    collections = []
    for name in names:
        collections.append({"name": name})
    z_library.create_collections(collections)

### Documents
def get_all_docs(z_library, collection_id: str) -> List[dict]:
    return z_library.everything(z_library.collection_items_top(collection_id))

def get_by_id(z_library, z_id: str) -> Dict:
    data = z_library.item(z_id)
    return data

def fetch_attachment_paths(z_library, parent_doc: Dict):
    parent_id = parent_doc["data"]["key"]
    child = z_library.children(parent_id)[0]

    return child["data"].get("path")

def upload_attachments(z_library, docs: List[Document]):
    print("Uploading attachments for {} Documents...".format(len(docs)))
    # TODO see if can do this in batch mode
    for doc in docs:
        if not doc.filepath:
            continue
        response = z_library.attachment_simple([doc.filepath], doc.get_z_id())
        # only need to do something with response if also want to store attachment id
        # TODO parse responses

def create_new_docs(z_library, docs: List[Document], add_attachments=False, collection_ids=None):
    ZOTERO_MAX = 50
    print("Creating {} Documents in Zotero...".format(len(docs)))
    all_templates = []
    for doc in docs:
        # select a template type from z_library.item_types()
        template = z_library.item_template("journalArticle")
        # set a title
        template["title"] = doc.title
        template["abstractNote"] = doc.abstract
        template["language"] = doc.language
        template["creators"] = doc.authors
        template["DOI"] = doc.doi
        template["ISSN"] = doc.issn
        template["url"] = doc.url
        if collection_ids:
            template["collections"] = collection_ids
        all_templates.append(template)

    # zotero only allows max (50 at time)
    failures = 0
    for i in range(0,len(all_templates), ZOTERO_MAX):
        response = z_library.create_items(all_templates[i:i+ZOTERO_MAX])
        # set zotero IDs for all docs
        for i, doc in enumerate(docs):
            if str(i) in response["success"]:
                doc.set_z_id(response["success"][str(i)])
        failures += len(response["failed"])

    print("{} new documents and {} failures".format(len(docs)-failures, failures) )
    success_docs = list(filter(lambda x: x.zotero_id, docs))
    if add_attachments:
        upload_attachments(z_library, list(filter(lambda x: x.filepath, success_docs)))

def update_doc_collections(z_library, doc_data: Dict, remove: Dict=None, add: Dict=None,
                           remove_all=False):
    """takes a document json and dicts of name2id for collections to add and remove, and updates in zotero"""
    # TODO work out how to support nested collections
    # TODO add handling for keyerrors in collection names
    if remove_all: # if True, removes document from all other collections save those specified
        collections_list = []
    else:
        collections_list = [col for col in doc_data["data"]["collections"]
                            if col not in list(remove.values())]
    collections_list.extend(list(add.values()))
    doc_data["data"]["collections"] = collections_list
    z_library.update_item(doc_data)
    print("Document {} has been updated from {} collections to {}".format(
        doc_data["data"]["title"], remove.keys(), remove.keys()))

### Misc
def remove_duplicates(z_library):
    """deletes duplicate documents found in Zotero. Conservatively, based on DOI and ISSN
    and abstract with no normalisation etc"""
    dois, issns, abstracts = set(), set(), set()
    collections = z_library.collections()
    collection_ids =  get_collection_IDs(collections)
    for col_id in collection_ids: # don't erase duplicates ACROSS collections
        all_docs = get_all_docs(z_library, col_id)
        deleted = 0
        for doc in all_docs:
            data = doc["data"]
            doi, issn, abstract = data.get("DOI"), data.get("ISSN"), data.get("abstractNote")
            if doi in dois or issn in issns or abstract in abstracts:
                z_library.delete_item(doc)
                deleted += 1
            else: # check that exist so don't add empty strings
                if doi:
                    dois.add(doi)
                if issn:
                    issns.add(issn)
                if abstract:
                    abstracts.add(abstract)
        print("{} docs were duplicates in collection {}".format(deleted, col_id), file=sys.stderr)
        #TODO write these documents to logs


def metadata_pretty_print(item):
    template = "Title: {}\n" \
               "Abstact: {}\n" \
               "Type:{}\n " \
               "DOI: {}\n"
    data = item["data"]
    title, abstract, doc_type, doi = data["title"], data["abstractNote"], data["itemType"], data["DOI"]

    print(template.format(title, abstract, doc_type, doi))


if __name__ == "__main__":
    args = setup_argparse()

    print("Reading config...")
    config = read_yaml_config(args.config_file)
    auth = config["auth"]

    # auth
    z_library = zotero.Zotero(auth["library_id"], auth["library_type"], auth["api_key"])
    all_documents = z_library.everything(z_library.top()) # gets around small API limit for what is returned
    all_collections = get_all_collections(z_library)

    example_id = "CTJ9YXEL"
    get_by_id(z_library, example_id)
    # cleanup
    #remove_duplicates(z_library)
    #sys.exit("done")

    # example print data from all items in a collection
    collection_i_want = "include"
    for item in all_collections:
        if item["data"]["name"] == collection_i_want:
            collection_key = item["key"]

    all_collection_docs = z_library.collection_items_top(collection_key)
    sample = all_collection_docs[0]
    children = z_library.children(sample["data"]["key"])
    for item in all_collection_docs:
        metadata_pretty_print(item)


    # Notes:
    #article = zot.fulltext_item(items[0]["key"]) #zot.file(items[0]["key"])
    #with os.scandir(config["input_dir"]) as source_dir:
    #     files = sorted([file.path for file in source_dir if file.is_file() and not file.name.startswith('.')])
