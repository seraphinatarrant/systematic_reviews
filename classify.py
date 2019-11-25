import argparse
from classifiers import ClassifierStrategy, SVMClassifier
from library_collections.document import Document, Label
from utils.corpus import Corpus
from utils.general_utils import read_yaml_config


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-c', dest='config_file', default='config/example_classifier.yaml',
                   help='a yaml config containing necessary API information')
    p.add_argument('-t', '--train', action='store_true', help='trains a new classifier')
    #p.add_argument('-d', dest='output_dir', default='outputs/', help='dir to write outputs to')
    return p.parse_args()

if __name__ == "__main__":
    args = setup_argparse()

    test_scraped_output = "scrapers/google_scholar/output/output.json"
    train_docs = Document.from_json(test_scraped_output, batch=True)
    Document.set_gold_labels(train_docs, [Label.exclude, Label.exclude, Label.include, Label.include])

    print("Reading config...")
    config = read_yaml_config(args.config_file)

    if not args.train:
        assert config["model"].get("pretrained", False), "if not training a new classifier, require a pretrained one to be specified"

    print("Reading classifier...")
    classifier = ClassifierStrategy.from_config(config)

    print("Reading document corpus...")
    corpus = Corpus(train_docs=train_docs)
    #corpus = Corpus.from_config(config)

    if args.train:
        labelled_corpus = Document.filter_gold_labels(corpus.train)
        assert labelled_corpus, "cannot train a classifier without any gold labels in the corpus"
        classifier.train_classifier(corpus.train)

    if bool(corpus.test):
        print("Classifying test corpus...")
        # TODO add tqdm for progress
        classifier.classify(corpus.test)