import argparse
import sys
from itertools import chain

from classifiers import ClassifierStrategy, SVMClassifier
from library_collections.document import Document, Label
from library_collections.lib_collection import Collection
from utils.corpus import Corpus
from utils.general_utils import read_yaml_config, split_data, load_pkl
from api.zotero_api import auth_zotero_library


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-c', dest='config_file', default='config/example_classifier.yaml',
                   help='a yaml config containing necessary API information')
    p.add_argument('-t', '--train', action='store_true', help='trains a new classifier')
    p.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                   help='verbose mode (prints more debug and info type stuff!)')
    #p.add_argument('-d', dest='output_dir', default='outputs/', help='dir to write outputs to')
    return p.parse_args()

if __name__ == "__main__":
    args = setup_argparse()

    # Silly test cases
    # test_scraped_output = "scrapers/google_scholar/output/output.json"
    # train_docs = Document.from_json(test_scraped_output, batch=True)
    # Document.set_gold_labels(train_docs, [Label.exclude, Label.exclude, Label.include, Label.include])

    print("Reading config...")
    config = read_yaml_config(args.config_file)
    print("Config settings:")
    print(config)

    ### Validation
    if not args.train:
        assert config["model"].get("pretrained", False), "if not training a new classifier, require a pretrained one to be specified. Did you mean to use the arg --train?"


    if config["corpus"].get("load_saved"):
        print("Loading pre-saved corpus...", file=sys.stderr)
        corpus = load_pkl(config["corpus"].get("load_saved"))
    else:
        if config["corpus"]["from_zotero"]:
            print("Loading documents from Zotero...")
            z_config_loc = config["corpus"].get("zotero_config")
            assert z_config_loc, "requires a zotero config location"
            collections = Collection.from_zotero(auth_zotero_library(read_yaml_config(z_config_loc)))
            all_docs = list(chain.from_iterable([col.documents for col in collections]))
        else:
            print("Reading documents")
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

    print("{} Training and {} Test Documents".format(len(corpus.train), len(corpus.test)), file=sys.stderr)

    print("Reading classifier...", file=sys.stderr)
    classifier = ClassifierStrategy.from_config(config)

    if args.train:
        labelled_corpus = Document.filter_gold_labels(corpus.train)
        assert labelled_corpus, "cannot train a classifier without any gold labels in the corpus"
        classifier.train_classifier(corpus.train)

    if bool(corpus.test):
        print("Classifying test corpus...")
        # TODO add tqdm for progress
        # TODO also make has_labels be set intelligently (based on config probs, or something)
        predictions = classifier.classify(corpus.test,
                                          has_labels=config["corpus"].get("test_labels"),
                                          confidence=config["classify"]["confidence_threshold"],
                                          thresh=config["classify"]["threshold"]
                                          )

        if args.verbose:
            print("Printing Results:")
            for doc, label_num in zip(corpus.test, predictions):
                print("{} was given label: {}.".format(doc, Label(label_num).name))
            print("-"*89)
            print("Printing Errors:")
            incorrect = filter(lambda d: d.gold_eq_predict, corpus.test)
            print("Ratio of incorrect/total: {}/{}".format(len(list(incorrect)), len(corpus.test)))
            for doc in corpus.test:
                print("doc: {} id: {} predicted_label: {} gold_label: {}".format(
                    doc, doc.get_id(), doc.predicted_label, doc.gold_label))


