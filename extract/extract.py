import argparse
import os
import spacy
import glob
import json

from operator import itemgetter
from pathlib import Path

import pandas as pd

nlp = spacy.load('test')


def add_categories_to_json(json_data, model=nlp):
    json_copy = dict(json_data)

    for section in json_copy['data']:
        if json_copy['data'].get(section):
            for e, sent in enumerate(model.pipe(json_copy['data'][section]['sentences'])):
                categories = sent.cats
                json_copy['data'][section]['sentences'][e] = {'text':sent.text, 'categories':categories}

    return json_copy


def get_top_sent_per_category(json_data, n=3):
    cats = ['SPECIES', 'DIAGNOSTIC_TEST', 'DATE_DATA', 'NUMBER_TESTED', 'SAMPLE', 'NUMBER_POSITIVE', 'DISEASE',
            'NOT_RELEVANT', 'STATE']
    sections = ['Abstract', 'Introduction', 'Methods', 'Results', 'Discussion']

    results = {k:[] for k in cats}

    seen_sents = set()

    for sect in sections:

        if json_data['data'].get(sect):
            sents = json_data['data'][sect]['sentences']
        else:
            continue

        for sent in sents:
            if sent['text'] in seen_sents:
                continue

            seen_sents.add(sent['text'])

            for cat, score in sent['categories'].items():
                if score > 0.0:
                    results[cat].append((score, sect, sent['text']))

    for k, v in results.items():
        results[k] = sorted(v, key=itemgetter(0), reverse=True)[0:n]

    results['bib_info'] = json_data['bib_info']

    return results

def create_csv(results):
    pass






if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract data from abstracts of papers')
    parser.add_argument('json_folder', help='Location of paper section JSONs')
    parser.add_argument('output_folder', help='Folder for storing the extracted data files')

    args = parser.parse_args()

    os.makedirs(Path(args.output_folder).expanduser(), exist_ok=True)

    json_files = (glob.glob(f"{args.json_folder}/*.json"))

    for file in json_files:
        with open(file) as f:
            json_data = json.load(f)

        json_data_augmented = add_categories_to_json(json_data)

        results = get_top_sent_per_category(json_data_augmented)

        with open(f"{args.output_folder}/{results['bib_info']['saved_pdf_name'].replace('.pdf', '.json')}", 'w') as f:
            json.dump(results, f, indent=5)
