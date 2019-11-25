import os
import argparse

from scrapers import search, grab

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-output', type=str, help='Filename for json output')
    parser.add_argument('-path', type=str, help='Path to save PDF files to. Will create if needed')
    parser.add_argument('-max', type=int, help='Max number of hits to return')
    parser.add_argument('-label', type=str, help='Label for search query')
    parser.add_argument('-search', type=str, help='Search terms to use')
    parser.add_argument('--range', nargs='+', type=int, default=(2015, 2019), help='Limit results to papers from these years, inclusive. Format: YYYY-YYYY')

    args = parser.parse_args()

    os.makedirs(args.path, exist_ok=True)

    print(f'Submitting {args.label} query...')

    searcher = search.GoogleScholar(label=args.label,
                                    search_phrase=args.search,
                                    date_range=args.range,
                                    results_folder=args.path,
                                    max_results=args.max)

    searcher.run()

    print('\tDone.')

    print(f'Grabbing PDFs...')

    for e, r_dict in enumerate(searcher.processed_results, 1):
        if r_dict['bib'].get('eprint'):
            grabber = grab.Grabber(url=r_dict['bib']['eprint'], save_location=args.path)
            grabber.run(filename=f"{e}.pdf")

    print('\tDone!')

    print('')
