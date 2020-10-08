import logging
logging.basicConfig(level=logging.ERROR)

import argparse
import glob
import json


# Import stuff for classify
# TODO

# Import for process pdf > json

from extract import process

# Import stuff for retrieval
import retrieval

# Import stuff for extraction

from extract import extract_ner
from transformers import pipeline, BertTokenizer
from spacy.lang.en import English

from IPython.core.display import display, HTML
import seaborn as sns

# print(dir(retrieval))
#
# print(dir(extract_ner))



if __name__ == '__main__':

    # Classify here?
    # TODO


    # Search and download

    parser = argparse.ArgumentParser()

    parser.add_argument('-engine', type=str, choices=['google', 'wos', 'pubmed', 'scopus'], help='Search engine to use')
    parser.add_argument('-json_file', type=str, help='Full path for where to save JSON output (filepath)')
    parser.add_argument('-pdf_folder', type=str, help='Path to save PDFs to (folderpath)')
    parser.add_argument('-max_results', type=int, help='Max number of hits to return', default=200)
    parser.add_argument('-label', type=str, help='Label for search query')
    parser.add_argument('-query', type=str, help='Search terms to use')
    parser.add_argument('-start_year', type=int, default=2015, help='Limit results to papers after this year, inclusive. Format: YYYY')
    parser.add_argument('-end_year', type=int, default=2020, help='Limit results to papers before this year, inclusive. Format: YYYY')

    # Arg for extract
    parser.add_argument('-model', help='Path to a trained spacy NER model')
    args = parser.parse_args()

    # Search

    print(f'Submitting {args.label} query...')

    engine = retrieval.engines[args.engine]

    searcher = engine(label=args.label,
                      search_phrase=args.query,
                      date_range=(args.start_year, args.end_year),
                      results_file=args.json_file,
                      max_results=args.max_results)

    #searcher.run()

    #retrieval.download(searcher, args.pdf_folder)

    # Process

    #process.process_pdf_folder(f"{args.pdf_folder}", f"{args.pdf_folder}/pdf_to_text")

    #process.combine_json_and_bibinfo(f"{args.pdf_folder}/pdf_to_text", f"{args.pdf_folder}")

    # Extraction

    tokenizer = BertTokenizer.from_pretrained(args.model,
                                              do_basic_tokenize=False,
                                              do_lower_case=False)

    ner = pipeline(task='ner', framework='pt',
                   model=args.model,
                   tokenizer=tokenizer,
                   grouped_entities=True)

    ner.ignore_labels = []

    nlp = English()
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer)

    json_files = (glob.glob(f"{args.pdf_folder}/pdf_to_text/sections_json/*.json"))

    for file in json_files:
        with open(file) as f:
            json_data = json.load(f)

        try:
            text = json_data['data']['Abstract']['text']
        except:
            continue

        text = "We tested 700 donkeys and 723 argabos in the Trayafag region of Armapia. The Amalakar Test was used to detect clinkora antibodies. The study ran from October 2018 to Septmeber 2019."

        sents = extract_ner.make_chunks(nlp, text, n=3)

        for sent in sents:

            try:
                e = ner(sent)
            except:
                continue

            colours = dict(sample_size='#1f77b4', study_date='#ff7f0e', region='#2ca02c', species='#d62728',
                           study_design='#9467bd', sample_type='#8c564b', diagnostic_test='#e377c2', disease='#7f7f7f',
                           individual_prevalence='#bcbd22', reference='#17becf', production_system='#aec7e8',
                           age='#bcbd22', statistical_analysis='#9467bd', herd_prevalence='#8c564b', ecosystem='#2ca02c')

            html_data = f"<br>{file}<br><br><div style='width:400px'>"

            for t in e:
                if t['entity_group'] == 'O':
                    html_data += f" <span style='font-family:calibri'>{t['word']}</span> "
                else:
                    style = f"font-weight:800;font-family:calibri;text-decoration:underline;color:{colours[t['entity_group'][2:]]}"
                    title = f"{t['entity_group']}  {t['score']:.5f}"
                    html_data += f" <span style='{style}' title='{title}'>{t['word']}</span> "

            html_data += "</div><br><hr>"


            with open(f'{args.pdf_folder}/extracted3.html', 'a', encoding='utf8') as f:
                f.write(html_data)
                f.write('\n\n')

        break
