import pickle
import yaml
import random
import string
from itertools import filterfalse

def read_yaml_config(config_file):
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

def make_id():
    id_length = 10 # we can change this to be longer based on volume of crawl
    alphanumeric = string.ascii_lowercase + string.digits
    return ''.join(random.choices(alphanumeric, k=id_length))