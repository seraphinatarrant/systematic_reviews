"""PSA this is very much in a TODO state as all API kinks have not yet been worked out"""

import argparse
from typing import List, Type, Dict

import sys
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

def get_collection_IDs(collections: List[Dict]) -> List[str]:
    return [col["key"] for col in collections]

def create_collections(z_library, names:List[str]):
    collections = []
    for name in names:
        collections.append({"name": name})

    z_library.create_collections(collections)

def get_all_docs(z_library, collection_id: str) -> List[dict]:
    return z_library.everything(z_library.collection_items_top(collection_id))

def fetch_attachment_paths(z_library, parent_doc: Dict):
    parent_id = parent_doc["data"]["key"]
    child = z_library.children(parent_id)[0]

    return child["data"].get("path")

def upload_attachments(z_library, docs: List[Document]):
    print("Uploading attachments for {} Documents...".format(len(docs)))
    # TODO see if can do this in batch mode
    for doc in docs:
        response = z_library.attachment_simple(doc.filepath, parentid=doc.get_id())
        # only need to do something with response if also want to store attachment id

def create_new_docs(z_library, docs: List[Document], add_attachments=False):
    print("Creating {} Documents...".format(len(docs)))
    all_templates = []
    for doc in docs:
        # select a template type from z_library.item_types()
        template = z_library.item_template("journalArticle")
        # set a title
        template["title"] = doc.title
        #TODO include other information extracted from pdf here
        all_templates.append(template)

    response = z_library.create_items(all_templates)
    doc_ids = response["key"] # TODO unsure if this is correct or nested (this is the format if create one item at a time)
    # TODO set correct ids for all Documents via set_id method

    if add_attachments:
        upload_attachments(z_library, docs)

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
    all_collections = z_library.collections()

    remove_duplicates(z_library)
    sys.exit("done")

    # example print data from all items in a collection
    collection_i_want = "WOS"
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
