
import csv
from typing import List

from api.zotero_api import auth_zotero_library, get_collection_names_and_IDs, get_all_collections, \
    get_by_id, update_doc_collections


def make_document_csv(all_documents:List, csv_path:str, csv_format:str):
    """write information from all documents to a csv, depending on format"""
    with open(csv_path, "w", newline="") as csvfile:
        if csv_format == "training_data":
            HEADERS = ["Title", "Abstract", "ID", "Zotero_ID", "Label"] # TODO move this to a global dict where headers are looked up from an enum
            csv_writer = csv.DictWriter(csvfile, fieldnames=HEADERS)
            csv_writer.writeheader()
            for doc in all_documents:
                csv_writer.writerow({
                    "Title": doc.title,
                    "Abstract": doc.abstract,
                    "ID": doc.get_id(),
                    "Zotero_ID": doc.zotero_id
                })
        elif csv_format == "classifier_output":
            HEADERS = ["Title", "Abstract", "ID", "Zotero_ID", "Label",
                       "Confidence", "Correction"]  # TODO move this to a global dict where headers are looked up from an enum
            csv_writer = csv.DictWriter(csvfile, fieldnames=HEADERS)
            csv_writer.writeheader()
            for doc in all_documents:
                csv_writer.writerow({
                    "Title": doc.title,
                    "Abstract": doc.abstract,
                    "ID": doc.get_id(),
                    "Zotero_ID": doc.zotero_id,
                    "Label": doc.predicted_label,
                    "Confidence": doc.confidence
                })

#TODO zotero upload to different training data folders per region
def read_document_csv(csv_path:str, csv_format:str, zotero_config):
    z_library = auth_zotero_library(zotero_config)
    # get zotero collections
    z_collections = get_collection_names_and_IDs(get_all_collections())

    with open(csv_path, "r", newline="") as csvfile:
        # TODO probably could compress both formats into one
        if csv_format == "training_data":
            # when training data is read in, the document may or may not exist in Zotero, and all previous collections (labels) will be wiped
            HEADERS = ["Title", "Abstract", "ID", "Zotero_ID", "Label"]  # TODO move this to a global dict where headers are looked up from an enum
            csv_reader = csv.DictReader(csvfile, fieldnames=HEADERS)
            for row in csv_reader:
                doc_data = get_by_id(z_library,row.get("Zotero_ID")) # TODO add handling for if doesn't exist
                update_doc_collections(z_library, doc_data,
                                       add={row["Label"]: z_collections[row["Label"]]}, remove_all=True)
            print("Updated {} documents".format(len(csv_reader)))

        if csv_format == "classifier_output":
            HEADERS = ["Title", "Abstract", "ID", "Zotero_ID", "Label",
                       "Confidence", "Correction"]  # TODO move this to a global dict where headers are looked up from an enum
            csv_reader = csv.DictReader(csvfile, fieldnames=HEADERS)
            corrections = 0
            for row in csv_reader:
                if row.get("Correction"):
                    # get zotero doc
                    doc_data = get_by_id(z_library,row.get("Zotero_ID"))
                    # update its collections with the correction
                    update_doc_collections(z_library, doc_data,
                                           {row["Label"]: z_collections[row["Label"]]},
                                           {row["Correction"]: z_collections[row["Correction"]]}
                                           )
                    corrections += 1
            print("{} documents corrected out of {} ({:.2f}%)".format(corrections, len(csv_reader),
                                                                      corrections*100/len(csv)))