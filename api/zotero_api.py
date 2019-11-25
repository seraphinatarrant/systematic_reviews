"""PSA this is very much in a TODO state as all API kinks have not yet been worked out"""

import argparse
from typing import List, Type
from pyzotero import zotero

from library_collections.document import Document
from utils.general_utils import read_yaml_config


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-c', dest='config_file', default='../config/zotero.yaml',
                   help='a yaml config containing necessary API information')
    return p.parse_args()

def create_collections(z_library, names:List[str]):
    collections = []
    for name in names:
        collections.append({"name": name})

    z_library.create_collections(collections)

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
        all_templates.add(template)

    response = z_library.create_items(all_templates)
    doc_ids = response["key"] # TODO unsure if this is correct or nested (this is the format if create one item at a time)
    # TODO set correct ids for all Documents via set_id method

    if add_attachments:
        upload_attachments(z_library, docs)

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

    # example print data from all items in a collection
    collection_i_want = "WOS"
    for item in all_collections:
        if item["data"]["name"] == collection_i_want:
            collection_key = item["key"]

    all_collection_docs = z_library.collection_items_top(collection_key)
    for item in all_collection_docs:
        metadata_pretty_print(item)


    # Notes:
    #article = zot.fulltext_item(items[0]["key"]) #zot.file(items[0]["key"])
    #with os.scandir(config["input_dir"]) as source_dir:
    #     files = sorted([file.path for file in source_dir if file.is_file() and not file.name.startswith('.')])
