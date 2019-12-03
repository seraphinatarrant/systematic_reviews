import argparse
import sys

from classifiers import ClassifierStrategy, SVMClassifier
from library_collections.document import Document, Label
from utils.corpus import Corpus
from utils.general_utils import read_yaml_config, split_data, load_pkl


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

    if not args.train:
        assert config["model"].get("pretrained", False), "if not training a new classifier, require a pretrained one to be specified. Did you mean to use the arg --train?"

    print("Reading documents")
    include_docs = Document.from_json(config["corpus"].get("include"), batch=True, verbose=args.verbose)
    Document.set_gold_labels(include_docs, Label.include, one_label=True)
    exclude_docs = Document.from_json(config["corpus"].get("exclude"), batch=True, verbose=args.verbose)
    Document.set_gold_labels(exclude_docs, Label.exclude, one_label=True)

    train_docs, test_docs = split_data(include_docs+exclude_docs)
    corpus = Corpus(train_docs=train_docs, test_docs=test_docs)
    corpus.save("corpus.pkl") # temporary test thing TODO something in config

    #corpus = load_pkl("corpus.pkl")
    print("{} Training and {} Test Documents".format(len(corpus.train), len(corpus.test)), file=sys.stderr)

    print("Reading classifier...")
    classifier = ClassifierStrategy.from_config(config)

    if args.train:
        labelled_corpus = Document.filter_gold_labels(corpus.train)
        assert labelled_corpus, "cannot train a classifier without any gold labels in the corpus"
        classifier.train_classifier(corpus.train)

    if bool(corpus.test):
        print("Classifying test corpus...")
        # TODO add tqdm for progress
        # TODO also make has_labels be set intelligently (based on config probs, or something)
        predictions = classifier.classify(corpus.test, has_labels=True)

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


