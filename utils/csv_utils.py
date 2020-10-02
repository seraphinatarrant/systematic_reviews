
import csv
import shutil
from collections import defaultdict
from typing import List

import os

from api.zotero_api import auth_zotero_library, get_collection_names_and_IDs, get_all_collections, \
    get_by_id, update_doc_collections, create_new_docs, remove_duplicates
from api.citoid_api import get_citation_data
from utils.general_utils import find_file, make_pdf_name
from library_collections.document import Document, FileType, Label, Source


### Globals for reading and writing CSVs
TRAINING_DATA_HEADERS = ["Title", "Abstract", "ID", "DOI", "Label", "Region"]
TRAINING_DATA_LABEL_MAPPING = {"e": "exclude", "i": "include"}
TEXT_EXTRACTION_HEADERS = ["ROW_NUMBER", "IDENTIFIER", "YEAR_PUBLICATION", "REFERENCE",
                           "START_DATE_DATA", "END_DATE_DATA", "STATE", "ECOSYSTEM",
                           "PRODUCTION_SYSTEM", "SPECIES", "AGE", "AGE_DETAIL", "DISEASE", "SAMPLE",
                           "DIAGNOSTIC_TEST", "MEASUREMENT", "NUMBER_POSITIVE", "NUMBER_TESTED",
                           "PERCENTAGE", "CALCULATION", "COMMENTS", "SOURCE"]
CLASSIFIER_HEADERS = ["Title", "Abstract", "ID", "DOI", "Label",
                       "Confidence", "Correction"]
PDF_DIR = "PDFs/"


def make_csv_name(doc_path, prefix):
    dir_path, filename = os.path.split(doc_path)
    filename, extension = os.path.splitext(filename)
    if prefix:
        filename = "{}_{}.csv".format(prefix, filename)
    else:
        filename = "{}.csv".format(filename)
    return os.path.join(dir_path, filename)


def make_document_csv(all_documents:List, csv_path:str, csv_format:str):
    """write information from all documents to a csv, depending on format"""
    with open(csv_path, "w", newline="") as csvfile:
        if csv_format == "training_data":
            csv_writer = csv.DictWriter(csvfile, fieldnames=TRAINING_DATA_HEADERS)
            csv_writer.writeheader()
            for doc in all_documents:
                csv_writer.writerow({
                    "Title": doc.title,
                    "Abstract": doc.abstract,
                    "ID": doc.get_id(),
                    "DOI": doc.doi
                })
        elif csv_format == "classifier_output":
            csv_writer = csv.DictWriter(csvfile, fieldnames=CLASSIFIER_HEADERS)
            csv_writer.writeheader()
            for doc in all_documents:
                csv_writer.writerow({
                    "Title": doc.title,
                    "Abstract": doc.abstract,
                    "ID": doc.get_id(),
                    "DOI": doc.zotero_id,
                    "Label": doc.predicted_label,
                    "Confidence": doc.confidence
                })

def read_document_csv(csv_path:str, csv_format:str, z_library):
    # get zotero collections so that have a name to arbitrary ID mapping
    z_collections = get_collection_names_and_IDs(get_all_collections(z_library), z_library)

    with open(csv_path, "r", newline="") as csvfile:
        # the label will be the name of the collection it is under
        # TODO probably could compress both formats into one
        if csv_format == "training_data":
            # when training data is read in, the document may or may not exist in Zotero, and all previous collections (labels) will be wiped
            csv_reader = csv.DictReader(csvfile, fieldnames=TRAINING_DATA_HEADERS)
            new_docs = defaultdict(list) #dict.fromkeys(TRAINING_DATA_LABEL_MAPPING.values(), []) # keys are labels
            for row in csv_reader:
                include_or_exclude = TRAINING_DATA_LABEL_MAPPING.get(row.get("Label"))
                if not include_or_exclude:
                    continue
                # "Labels" are encoded in zotero basically via collections
                label = include_or_exclude
                if row.get("Region"):
                    label = label + "_" + row.get("Region")
                if row.get("Zotero_ID"): # doc already exists in zotero, and we want to update the label it has/collections it is in
                    doc_data = get_by_id(z_library,row.get("Zotero_ID")) # TODO add handling for if doesn't exist remotely
                    update_doc_collections(z_library, doc_data,
                                           add={label: z_collections[label]},
                                           remove_all=True)
                elif row.get("DOI"): # add new document to Zotero
                    doi = row.get("DOI")
                    citation_data = get_citation_data(doi)
                    doc_label = Label.include if include_or_exclude == "include" else Label.exclude
                    # TODO check if it exists in zotero and if so update doc collections and if not make new
                    new_doc = Document(source=Source.journal, file_type=FileType.pdf, doi=doi)
                    new_doc.set_info_from_citation(citation_data)
                    new_doc.set_gold_label(doc_label)
                    new_doc.filepath = find_file(PDF_DIR, make_pdf_name(doi))
                    new_docs[label].append(new_doc)

                # check if anything in new_docs, and upload to zotero
            for label in new_docs:
                # TODO temporary while zotero upload is broken -- make a new folder and move pdfs to it so can manually upload
                #make label if doesnt exist
                label_dir = os.path.join(PDF_DIR, label)
                if not os.path.exists(label_dir):
                    os.makedirs(label_dir)
                print("{} docs in category {}".format(len(new_docs[label]), label))
                for doc in new_docs[label]:
                    doc_name = os.path.split(doc.filepath)[1]
                    try:
                        shutil.copyfile(doc.filepath, os.path.join(label_dir, doc_name))
                    except:
                        print(doc.filepath, doc_name)
                    #cp_command = "cp {} {}".format(doc.filepath, label_dir)
                    #os.system(cp_command)
            #     create_new_docs(z_library, new_docs[label], add_attachments=True,
            #                     collection_ids=[z_collections[label]])
            #     # run remove duplicates
            #     remove_duplicates(z_library)
            #
            # print("Updated {} documents".format(len(new_docs.values())))

        if csv_format == "classifier_output":
            csv_reader = csv.DictReader(csvfile, fieldnames=CLASSIFIER_HEADERS)
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
def combine_csvs(dirpath):
    """combines all csvs in a directory that have the same headers into one csv with the dirname"""
    HEADERS = ["Title", "Abstract", "ID", "DOI", "Label"]
    with os.scandir(dirpath) as source_dir:
        parent_path, dirname = os.path.split(dirpath) # grab parent directory of files
        csvs = [entry.path for entry in source_dir if entry.is_file() and entry.name.endswith('.csv')
                and not entry.name.startswith(".")]
    with open(os.path.join(parent_path,dirname+".csv"), "w", newline="") as csv_out:
        writer = csv.DictWriter(csv_out, fieldnames=HEADERS)
        writer.writeheader()
        for c in csvs:
            with open(c, "r", newline='',) as csv_in:
                reader = csv.DictReader(csv_in)
                for row in reader:
                    writer.writerow(rowdict=row)
                # TODO validate that correct fieldnames exist

# def split_csv_by_label(csv_path):
#     include_lines, exclude_lines = [], []
#     csv_prefix = os.path.splitext(csv_path)[0]
#     with open(csv_path, "r", newline='') as csv_in:
#         csv_reader = csv.DictReader(csv_in, fieldnames=TRAINING_DATA_HEADERS)
#         LABEL_HEADER = TRAINING_DATA_HEADERS[-1]
#         for row in csv_reader:
#             label = row.get(LABEL_HEADER)
#             if label == "i":
#                 include_lines.append(row)
#             elif label == "e":
#                 exclude_lines.append(row)
#             else:
#                 continue
#         print("Total: includes {}, excludes {}".format(len(include_lines), len(exclude_lines)))
#     with open(csv_prefix + "_include.csv", "w", newline='') as csv_include,
#         open(csv_prefix + "_exclude.csv", "w", newline='') as csv_exclude:
#         for row in include_lines:
#
#




def format_dict_values(d: dict):
    for key in d:
        if type(d[key]) == list:
            if d[key]:
                d[key] = ",".join(d[key])
            else:
                d[key] = ""


def write_csv_from_dicts(csv_path: str, list_of_dicts: List[dict]):
    with open(csv_path, "w", newline='') as csv_out:
        csv_w = csv.DictWriter(csv_out, fieldnames=TEXT_EXTRACTION_HEADERS)
        csv_w.writeheader()
        row_num = 1
        for d in list_of_dicts:
            d["ROW_NUMBER"] = row_num
            row_num += 1
            format_dict_values(d)
            csv_w.writerow(d)


if __name__ == "__main__":
    directories = [
        "PDFs/new_training_data_v2/wos_Nigeria/json", "PDFs/new_training_data_v2/pubmed_Nigeria/json",
        "PDFs/new_training_data_v2/wos_Tanzania/json", "PDFs/new_training_data_v2/pubmed_Tanzania/json",
        "PDFs/new_training_data_v2/pubmed_Ethiopia/json"
                   ]
    for directory in directories:
        combine_csvs(directory)