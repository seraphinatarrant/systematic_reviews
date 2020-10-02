import pickle

import glob
import yaml
import random
import string
from typing import Dict
from itertools import filterfalse
from sklearn.model_selection import train_test_split


def read_yaml_config(config_file: str) -> Dict:
    return yaml.load(open(config_file), Loader=yaml.FullLoader)

def bool_partition(func, iterable):
    """takes a function that return a bool and and iterable returns two generators from iterable, the true and the false"""
    return list(filter(func, iterable)), list(filterfalse(func, iterable))

def save_pkl(things, path: str):
    with open(path, "wb") as fout:
        pickle.dump(things,fout)

def load_pkl(path: str):
    with open(path, "rb") as fin:
        things = pickle.load(fin)
    return things

def make_id() -> str:
    id_length = 10 # we can change this to be longer based on volume of crawl
    alphanumeric = string.ascii_lowercase + string.digits
    return ''.join(random.choices(alphanumeric, k=id_length))

def split_data(data, train_percent=0.85, test_percent=0.15):
    train, test = train_test_split(data, train_size=train_percent, shuffle=True)
    return train, test

def make_pdf_name(doi):
    return doi.replace('/', '_') + '.pdf'

#TODO remove rootdir
def find_file(rootdir, filename):
    file = glob.glob("**/"+filename, recursive=True)
    if file:
        return file[0] # arbitrarily pick one if there's more than one of the same file
    else:
        return ""




