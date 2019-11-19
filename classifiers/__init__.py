import argparse
import yaml
import sys


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-c', dest='config_file', default='../config/zotero.yaml',
                   help='a yaml config containing necessary API information')
    #p.add_argument('-d', dest='output_dir', default='../outputs/D4/', help='dir to write output summaries to')
    #p.add_argument('-m', dest='model_path', default='', help='path for a pre-trained embedding model')
    return p.parse_args()


def read_yaml_config(config_file):
    return yaml.load(open(config_file))


if __name__ == "__main__":
    args = setup_argparse()

    print("Reading config...")
    config = read_yaml_config(args.config_file)