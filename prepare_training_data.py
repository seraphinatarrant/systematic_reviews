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

from utils.general_utils import read_yaml_config
from utils.csv_utils import make_document_csv, read_document_csv
from library_collections.lib_collection import Document


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-c', dest='config_file', default='config/prep_train_data.yaml',
                   help='a yaml config containing necessary information to prepare training data')
    return p.parse_args()


if __name__ == "__main__":
    args = setup_argparse()
    z_config_file = "config/zotero_personal.yaml"
    z_config = read_yaml_config(z_config_file)
    config = read_yaml_config(args.config_file)
    print("Extracting metadata...")
    all_documents = Document.from_json(config.get("input_json"), batch=True)
    # TODO create all documents in Zotero and then set their zotero_ids
    print("Writing a csv of {} documents".format(len(all_documents)))
    make_document_csv(all_documents, config.get("csv_path", "."), "training_data")
    print("Loading in CSV")
    # TODO test corrections and also loading in training data

