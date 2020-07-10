import time
import datetime

import argparse
import retrieval

import pandas as pd


def do_query(engine, json_file, max_results, label, year_range, query, pdf_folder):

    searcher = engine(label=label,
                      search_phrase=query,
                      date_range=year_range,
                      results_file=json_file,
                      max_results=max_results)

    searcher.run()

    retrieval.grab.download(searcher, pdf_folder)


engines = {'google': retrieval.GoogleScholar, 'wos': retrieval.WoS, 'scopus': retrieval.Scopus, 'pubmed': retrieval.PubMed}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-mode', required=True, type=str, choices=['single', 'batch'], help='Submit single specified query, or use a CSV file of queries.')

    parser.add_argument('-csv_file', type=str, help="CSV of queries, one per line. Columns should be {'engine', 'json_file', 'max_results', 'label', 'start_year', 'end_year', 'query', 'pdf_folder'}")

    parser.add_argument('-engine', type=str, choices=['google', 'wos', 'pubmed', 'scopus'], help='Search engine to use')
    parser.add_argument('-json_file', type=str, help='Full path for where to save JSON output (filepath)')
    parser.add_argument('-pdf_folder', type=str, help='Path to save PDFs to (folderpath)')
    parser.add_argument('-max_results', type=int, help='Max number of hits to return', default=200)
    parser.add_argument('-label', type=str, help='Label for search query')
    parser.add_argument('-query', type=str, help='Search terms to use')
    parser.add_argument('-start_year', type=int, default=2015, help='Limit results to papers after this year, inclusive. Format: YYYY')
    parser.add_argument('-end_year', type=int, default=2020, help='Limit results to papers before this year, inclusive. Format: YYYY')

    args = parser.parse_args()

    

    if args.mode == 'single':
        print(f'Submitting {args.label} query...')

        engine = engines[args.engine]

        searcher = engine(label=args.label,
                          search_phrase=args.query,
                          date_range=(args.start_year, args.end_year),
                          results_file=args.json_file,
                          max_results=args.max_results)

        searcher.run()

        retrieval.grab.download(searcher, args.pdf_folder)

    if args.mode == 'batch':
        if not args.csv_file:
            parser.error('No input CSV file provided - required for mode=batch')
        items = pd.read_csv(args.csv_file)

        if set(items.columns) != {'engine', 'json_file', 'max_results', 'label', 'start_year', 'end_year', 'query', 'pdf_folder'}:
            parser.error(f"CSV file has incorrect columns.\n\
                    Expected: {sorted(['engine', 'json_file', 'max_results', 'label', 'start_year', 'end_year', 'query', 'pdf_folder'])}\n\
                    Got     : {sorted(list(items.columns))}\n\
                    Extra   : {[i for i in items.columns if i not in ['engine', 'json_file', 'max_results', 'label', 'start_year', 'end_year', 'query', 'pdf_folder']]}\n\
                    Missing : {[i for i in ['engine', 'json_file', 'max_results', 'label', 'start_year', 'end_year', 'query', 'pdf_folder'] if i not in items.columns]}")


        # WOS has a rate limit of 1 request per minute.
        # Problematic when queries finish too fast, such as when few results.

        for _, r in items.iterrows():

            start_t = datetime.datetime.now()

            do_query(engine = engines[r.engine],
                     json_file = r.json_file,
                     max_results = int(r.max_results),
                     label = r.label,
                     year_range = (r.start_year, r.end_year),
                     query = r.query,
                     pdf_folder = r.pdf_folder)

            finish_t = datetime.datetime.now()

            delta = finish_t - start_t

            if delta.seconds <= 60:
                time.sleep(80 - delta.seconds)








