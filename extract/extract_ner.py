import logging
logging.basicConfig(level=logging.ERROR)

import argparse
import os
import spacy
import glob
import json

from collections import defaultdict, Counter
from operator import itemgetter
from pathlib import Path

import pandas as pd

from transformers import pipeline, BertTokenizer
from spacy.lang.en import English

from IPython.core.display import display, HTML
import seaborn as sns


def full_extract(model, json_data):
    '''
    model : trained transformer NER model
    json_data : the text extracted from a PDF via process.py

    Use the NER model to label entities within the text.

    Return a long format dataframe.
    Each row is one extracted entity, its label, textual context, section it was found in
    '''

    full_data = []

    for section_name, section_contents in json_data['data'].items():
        doc = model(section_contents['text'])

        for entity in doc.ents:
            context = str(doc[entity.start-5:entity.end+5])

            if entity.label_ in {'species', 'diagnostic_test', 'disease', 'sample_type'}:
                text = entity.text.lower()
            else:
                text = entity.text
            
            full_data.append([section_name, entity.label_, text, context])

    full_data = pd.DataFrame(full_data, columns=['section', 'label', 'text', 'context'])

    for k,v in json_data['bib_info'].items():
        full_data['_' + k] = v

    return full_data


def summarise(full_data, json_data):
    '''
    Take the long format full_data dataframe and arrange it such that for each
    entity label, it shows the extracted texts, their counts and their proportion
    in terms of all texts for that label.
    '''
    summary = pd.DataFrame(full_data.groupby(['label']).text.value_counts(sort='descending'))
    
    props = full_data.groupby(['label']).text.value_counts(sort='descending', normalize=True).values
    sums = full_data.groupby(['label']).text.value_counts(sort='descending', normalize=False).groupby('label').sum()
    
    summary.reset_index(level=0, inplace=True)
    summary.columns = ['label', 'count']
    summary['proportion'] = props
    summary['total_items_for_label'] = ''


    summary = summary.reset_index().set_index('label')

    summary.loc[sums.index, 'total_items_for_label'] = sums

    summary = summary.reset_index()

    for k,v in json_data['bib_info'].items():
        summary['_' + k] = v

    return summary


def make_chunks(nlp, text, n=4):
    doc = nlp(text)
    sents = [i.text for i in doc.sents]
    sents = [" ".join(sents[i:i + n]) for i in range(0, len(sents), n)]

    return sents


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract data from papers')
    parser.add_argument('json_folder', help='Location of folder containing paper section JSONs')
    parser.add_argument('output_folder', help='Path for saving CSV outputs')
    parser.add_argument('model', help='Path to a trained spacy NER model')

    args = parser.parse_args()

    tokenizer = BertTokenizer.from_pretrained(args.model,
                                              do_basic_tokenize=False,
                                              do_lower_case=False)

    ner = pipeline(task='ner', framework='pt',
                   model=args.model,
                   tokenizer=tokenizer,
                   grouped_entities=True)

    nlp = English()
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer)

    os.makedirs(Path(args.output_folder).expanduser(), exist_ok=True)

    json_files = (glob.glob(f"{args.json_folder}/*.json"))

    for file in json_files:
        with open(file) as f:
            json_data = json.load(f)

        text = json_data['data']['Abstract']['text']

        sents = make_chunks(text, n=5)

        for sent in sents:

            e = ner(sent)

            html_data = "<div style='width:400px'>"

            for t in e:
                if t['entity_group'] == 'O':
                    html_data += f" <span'>{t['word']}</span> "
                else:
                    style = f"text-decoration:underline;color:{colours[t['entity_group'][2:]]}"
                    title = f"{t['entity_group']}  {t['score']:.5f}"
                    html_data += f" <span style='{style}' title='{title}'>{t['word']}</span> "

            html_data += "</div>"
            display(HTML(html_data))






        # full_data = full_extract(nlp, json_data)
        #
        # summary = summarise(full_data, json_data)
        #
        # csv_stem = json_data['bib_info']['saved_pdf_name'].replace('.pdf', '')
        #
        # full_data.to_csv(f"{args.output_folder}/{csv_stem}_full_extract.csv", index=None)
        #
        # summary.to_csv(f"{args.output_folder}/{csv_stem}_summary_extract.csv", index=None)

