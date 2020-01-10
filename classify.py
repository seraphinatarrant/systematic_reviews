import argparse
import sys
from itertools import chain, filterfalse
import logging
from datetime import datetime

import os

from classifiers import ClassifierStrategy, SVMClassifier
from library_collections.document import Document, Label
from library_collections.lib_collection import Collection
from utils.corpus import Corpus
from utils.general_utils import read_yaml_config, split_data, load_pkl
from api.zotero_api import auth_zotero_library, remove_duplicates


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-c', dest='config_file', default='config/example_classifier.yaml',
                   help='a yaml config containing necessary API information')
    p.add_argument('-t', '--train', action='store_true', help='trains a new classifier')
    p.add_argument('-l', '--log', dest='loglevel', default="INFO",
                   choices=["INFO", "DEBUG", "WARNING", "ERROR","CRITICAL"])
    p.add_argument('--log_dir', default="logs/", help="location to store log files")
    return p.parse_args()

if __name__ == "__main__":
    args = setup_argparse()
    logging.getLogger('matplotlib.font_manager').disabled = True
    script_name = os.path.basename(sys.argv[0])
    log_path = os.path.join(args.log_dir,"{}: {}: {}".
                                         format(script_name, args.loglevel, str(datetime.now())))
    logging.basicConfig(filename=log_path,
                        format="%(levelname)s:%(message)s",
                        level=getattr(logging, args.loglevel))

    # Silly test cases
    # test_scraped_output = "scrapers/google_scholar/output/output.json"
    # train_docs = Document.from_json(test_scraped_output, batch=True)
    # Document.set_gold_labels(train_docs, [Label.exclude, Label.exclude, Label.include, Label.include])

    logging.info("Reading config...")
    config = read_yaml_config(args.config_file)
    logging.info("Config settings:\n{}".format(config))

    ### Validation
    if not args.train:
        assert config["model"].get("pretrained", False), "if not training a new classifier, require a pretrained one to be specified. Did you mean to use the arg --train?"


    if config["corpus"].get("load_saved"):
        logging.info("Loading pre-saved corpus...")
        corpus = load_pkl(config["corpus"].get("load_saved"))
    else:
        if config["corpus"]["from_zotero"]:
            logging.info("Loading documents from Zotero...")
            z_config_loc = config["corpus"].get("zotero_config")
            assert z_config_loc, "requires a zotero config location"
            z_library = auth_zotero_library(read_yaml_config(z_config_loc))
            # print("Cleaning Zotero duplicates first...")
            # remove_duplicates(z_library)
            collections = Collection.from_zotero(z_library)
            all_docs = list(chain.from_iterable([col.documents for col in collections]))
        else:
            logging.info("Reading documents")
            include_docs = Document.from_json(config["corpus"].get("include"), batch=True, verbose=args.verbose)
            Document.set_gold_labels(include_docs, Label.include, one_label=True)
            exclude_docs = Document.from_json(config["corpus"].get("exclude"), batch=True, verbose=args.verbose)
            Document.set_gold_labels(exclude_docs, Label.exclude, one_label=True)
            all_docs = include_docs+exclude_docs

        # filter out docs with no: 1) text or abstract data 2) gold labels (only if training)
        if args.train:
            #all_docs = Document.filter_fields(all_docs, [Document.gold_label, Document.abstract])
            all_docs = Document.filter_gold_labels(all_docs)
            all_docs = Document.filter_failed_parses(all_docs)


        train_docs, test_docs = split_data(all_docs)
        corpus = Corpus(train_docs=train_docs, test_docs=test_docs)
        save_loc = config["corpus"].get(SVMClassifier.SAVE_LOC_KEY, "corpus.pkl")
        corpus.save(save_loc)

    logging.info("{} Training and {} Test Documents".format(len(corpus.train), len(corpus.test)))

    logging.info("Reading classifier...")
    classifier = ClassifierStrategy.from_config(config)

    if args.train:
        labelled_corpus = Document.filter_gold_labels(corpus.train)
        assert labelled_corpus, "cannot train a classifier without any gold labels in the corpus"
        classifier.train_classifier(corpus.train)

    if bool(corpus.test):
        logging.info("Classifying test corpus of {} documents...".format(len(corpus.test)))
        predictions = classifier.classify(corpus.test,
                                          has_labels=config["corpus"].get("test_labels"),
                                          confidence=config.get("classify", {}).get("confidence_threshold"),
                                          thresh=config.get("classify", {}).get("threshold")
                                          )


        logging.debug("Printing Results:")
        for doc, label_num in zip(corpus.test, predictions):
            logging.debug("{} was given label: {}.".format(doc, Label(label_num).name))
        logging.debug("-"*89)
        logging.debug("Printing Errors:")
        incorrect = filterfalse(lambda d: d.gold_eq_predict, corpus.test)
        logging.debug("Ratio of incorrect/total: {}/{}".format(len(list(incorrect)), len(corpus.test)))
        for doc in incorrect:
            logging.debug("doc: {} id: {} predicted_label: {} gold_label: {}".format(
                doc, doc.get_id(), doc.predicted_label, doc.gold_label))


