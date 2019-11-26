import pickle
import yaml
import random
import string
from itertools import filterfalse
from sklearn.model_selection import train_test_split

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

def split_data(data, train_percent=0.8, test_percent=0.2):
    train, test = train_test_split(data, train_size=train_percent, shuffle=True)
    return train, test