"""
A script that takes scraped data and prepares it in a format that makes it easier for humans
to classify documents (in order to create training data).
Steps:
- imports JSON and PDFs from Scraping
- extracts metadata
- creates a csv of the information

In future, may also do an autoupload to zotero (though so easy to do manually...)
"""

import argparse
import logging
import os
import sys
from datetime import datetime

from api.zotero_api import create_new_docs, auth_zotero_library
from utils.general_utils import read_yaml_config
from utils.csv_utils import make_document_csv, read_document_csv, make_csv_name, combine_csvs
from library_collections.lib_collection import Document


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-c', dest='config_file', default='config/prep_train_data.yaml',
                   help='a yaml config containing necessary information to prepare training data')
    p.add_argument('-zc', dest='zotero_config_file', default='config/zotero_personal.yaml',
                   help='a yaml config for zotero auth')
    p.add_argument('-l', '--log', dest='loglevel', default="INFO",
                   choices=["INFO", "DEBUG", "WARNING", "ERROR","CRITICAL"])
    p.add_argument('--log_dir', default="logs/", help="location to store log files")
    return p.parse_args()


if __name__ == "__main__":
    args = setup_argparse()
    script_name = os.path.basename(sys.argv[0])
    log_path = os.path.join(args.log_dir, "{}: {}: {}".
                            format(script_name, args.loglevel, str(datetime.now())))
    logging.basicConfig(filename=log_path,
                        format="%(levelname)s:%(message)s",
                        level=getattr(logging, args.loglevel))

    z_config = read_yaml_config(args.zotero_config_file)
    z_library = auth_zotero_library(z_config)
    config = read_yaml_config(args.config_file)
    # check what type of training data reading in
    if config.get("input_json"):
        input_docs = [config.get("input_json")]
    elif config.get("input_dir"): # search for all json files in directory and subdirs.
        input_docs = []
        for dirpath, dirnames, filenames in os.walk(config.get("input_dir")):
            if filenames:
                for filename in filenames:
                    if os.path.splitext(filename)[1] != ".json":
                        continue
                    input_docs.append(os.path.join(dirpath, filename))
    else:
        sys.exit("Need to specify 'input_json' or 'input_dir' in config file")

    for doc in input_docs:
        print("Extracting metadata for {}...".format(doc))
        all_documents = Document.from_json(doc, batch=True)
        #create_new_docs(z_library, all_documents, add_attachments=True, collection_ids=)
        if not all_documents:
            print("No data contained in {}, skipping".format(doc))
            continue
        if config.get("require_abstracts", False):
            #remove ones without abstracts and print in case we want to do something about it
            valid_documents = list(filter(lambda d: d.abstract, all_documents))
            if len(all_documents) - len(valid_documents) > 0:
                print("{} of {} documents were fetched but their abstracts were not".format(
                    len(all_documents) - len(valid_documents), len(valid_documents)), file=sys.stderr)

        print("Writing a csv of {} documents".format(len(all_documents)))
        csv_path = make_csv_name(doc, config.get("csv_prefix"))
        make_document_csv(all_documents, csv_path, "training_data")

    #print("Loading in CSV")
    # TODO test corrections and also loading in training data

