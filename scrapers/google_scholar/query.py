import os
import json
import tqdm
import scholarly
import argparse
import requests


def query_with_year(search_phrase, start=2015, end=2019):
    custom_url = f"/scholar?q={search_phrase}&hl=en&as_sdt=0%2C5&as_ylo={start}&as_yhi={end}"
    return scholarly.search_pubs_custom_url(custom_url)


def query(search_phrase):
    return scholarly.search_pubs_query(search_phrase)


def get_pdf(url):
    r = requests.get(url, allow_redirects=True)

    if 'pdf' in r.headers.get('content-type').lower():
        return r.content

    return None

def write_pdf(path, pdf):
    with open(path, 'wb') as f:
        f.write(pdf)


def parse_results(query_results, output, path, n):
    with tqdm.tqdm(total=n) as pbar:
        for e, r in enumerate(query_results, 1):

            try:
                r.fill()
            except:
                # 403, probably
                pass

            r_dict = r.__dict__

            if type(r_dict['bib']['abstract']) != str:
                r_dict['bib']['abstract'] = r_dict['bib']['abstract'].text

            with open(f"{path}/{output}", 'a') as o:
                json.dump(r_dict, o, indent=5)
                o.write('\n')
                pbar.update(1)

            if r_dict['bib'].get('eprint'):
                url = r_dict['bib']['eprint']

                try:
                    pdf = get_pdf(url)

                    if pdf:
                        save_path = f"{path}/{r_dict['bib']['title']}.pdf"
                        write_pdf(save_path, pdf)
                except:
                    pass



            if e == n:
                break

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-output', type=str, help='Filename for json output')
    parser.add_argument('-path', type=str, help='Path to save PDF files to. Will create if needed')
    parser.add_argument('-max', type=int, help='Max number of hits to return')
    parser.add_argument('-label', type=str, help='Label for search query')
    parser.add_argument('-search', type=str, help='Search terms to use')
    parser.add_argument('-range', type=str, help='Limit results to papers from these years, inclusive. Format: YYYY-YYYY')

    args = parser.parse_args()

    os.makedirs(args.path, exist_ok=True)

    print(f'Submitting {args.label} query...')

    if args.range:
        try:
            start, end = args.range.split('-')
        except:
            raise ValueError('Year range is not in correct format. Format: YYYY-YYYY')
        results = query_with_year(args.search, start=start, end=end)
    else:
        results = query(args.search)

    print('\tDone.')

    print(f'Parsing results to file...')

    parse_results(results, output=args.output, path=args.path, n=args.max)

    print('Done!')
