import time
import random
import json
import tqdm
import scholarly
import argparse


def query_with_year(search_phrase, start=2015, end=2019):
    custom_url = f"/scholar?q={search_phrase}&hl=en&as_sdt=0%2C5&as_ylo={start}&as_yhi={end}"
    return scholarly.search_pubs_custom_url(custom_url)

def query(search_phrase):
    return scholarly.search_pubs_query(search_phrase)

def convert_to_json(result):
    data = dict(result.bib)
    data['citedby'] = result.citedby
    data['id_scholarcitedby'] = result.id_scholarcitedby
    data['url_scholarbib'] = result.url_scholarbib

    return data

def parse_results(query_results, n):
    with tqdm.tqdm(total=n) as pbar:
        for e, r in enumerate(query_results, 1):

            r_json = convert_to_json(r)

            with open('test.json', 'a') as output:
                json.dump(r_json, output)
                output.write('\n')
                pbar.update(1)

            time.sleep(random.randint(3,8))

            if e == n:
                break

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-max', type=int)
    parser.add_argument('-label', type=str)
    parser.add_argument('-search', type=str)

    args = parser.parse_args()


    print(f'Submitting {args.label} query...')
    results = query(args.search)
    print('\tDone.')

    print(f'Parsing results to file...')
    parse_results(results, n=args.max)
    print('Done!')