import os
import json
import tqdm
import datetime

from xml.etree import ElementTree as ET

import scholarly  # Google Scholar
import pybliometrics as pb # Scopus
import wos # Web of Knowledge
import pymed # PubMed

import sys

sys.path.append('..')
from api.citoid_api import get_citation_data


class Query:
    def __init__(self, label: str, search_phrase: str, date_range: tuple, results_dir: str, results_file: str, max_results: int):
        self.label = label
        self.search_phrase = search_phrase
        self.start_date, self.end_date = date_range
        if results_file.endswith('.json'):
            self.results_file = results_file.split('.json')[0]
        else:
            self.results_file = results_file

        os.makedirs(results_dir, exist_ok=True)
        self.results_dir = results_dir

        self.n = max_results

        self.processed_results = None

        self.source = None

        self.data = {'metadata':{'source':None,
                                         'label':self.label,
                                         'search_phrase':self.search_phrase,
                                         'date_range':[self.start_date, self.end_date]
                                 },
                     'results':None
                    }


    def search(self):
        raise NotImplementedError

    def process_results(self, search_results):
        raise NotImplementedError

    def save_to_json(self):
        now = datetime.datetime.now()
        stamp = now.strftime("%d-%b-%Y_%H-%M-%S")

        print(f"Saving results to: {stamp}_{self.results_file}.json")

        with open(f"{self.results_dir}/{stamp}_{self.results_file}.json", 'w') as o:
            json.dump(self.data, o, indent=5)

        print(f"Done!")

    def run(self):
        self.search_results = self.search()

        if self.search_results:
            self.data['results'] = self.process_results(self.search_results)
        else:
            print('No results found...')

        self.save_to_json()


class GoogleScholar(Query):
    def __init__(self, label: str, search_phrase: str, date_range: tuple, results_folder: str, max_results: int):
        super().__init__(label, search_phrase, date_range, results_folder, max_results)

        self.source = 'Google_Scholar'
        self.data['metadata']['source'] = 'Google_Scholar'

    def search(self):
        if all([self.start_date, self.end_date]):
            custom_url = f"/scholar?q={self.search_phrase}&hl=en&as_sdt=0%2C5&as_ylo={self.start_date}&as_yhi={self.end_date}"
            results = scholarly.search_pubs_custom_url(custom_url)
        else:
            results = scholarly.search_pubs_query(self.search_phrase)

        if results:
            return results
        else:
            raise Exception("No results were returned. This is likely due to rate limits!")

    def process_results(self, search_results, save, n):
        all_dicts = []

        with tqdm.tqdm(total=n) as pbar:
            for e, r in enumerate(search_results, 1):
                try:
                    r.fill()
                except:
                    # Probably a 403 error on accessing the Bibtex URL
                    # Should make this more specific.
                    pass

                r_dict = r.__dict__

                if type(r_dict['bib']['abstract']) != str:
                    r_dict['bib']['abstract'] = r_dict['bib']['abstract'].text

                all_dicts.append(r_dict)

                pbar.update(1)

                if e == n:
                    break

        return all_dicts


class WoS(Query):
    def __init__(self, label: str, search_phrase: str, date_range: tuple, results_dir: str, results_file: str, max_results: int):
        super().__init__(label, search_phrase, date_range, results_dir, results_file, max_results)
        self.original_search_phrase = search_phrase


        self.start_date = date_range[0]
        self.end_date = date_range[1]

        if all([self.start_date, self.end_date]):
            self.search_phrase = f"TS=({search_phrase}) AND PY=({self.start_date}-{self.end_date})"
        else:
            self.search_phrase = f"TS=({search_phrase})"

        self.source = 'WoS'
        self.data['metadata']['source'] = 'WoS'



    def run(self):
        self.search_results = self.search()

        if self.search_results:
            self.data['results'] = self.process_results(self.search_results)
        else:
            print('No results found...')

        self.save_to_json()


    def search(self):
        client = wos.WosClient(lite=True)

        offset = 1

        count = 100

        if self.n < count:
            count = self.n

        all_results = []

        with client as c:
            result = wos.utils.query(c, self.search_phrase, count=count, offset=offset)

            tree = ET.fromstring(result)

            max_total = int(tree.find('recordsFound').text)

            print(f"Total matches found: {max_total}")

            for r in tree.findall('.//records'):
                if len(all_results) == self.n:
                    break
                else:
                    all_results.append(r)

            loops = round(max_total / count)

            if loops in {0,1}:
                # We only needed one loop, so have got all we can, so return it.
                print(f'\tTotal papers grabbed: {len(all_results)}')
                return all_results

            for loop in range(loops - 1):
                offset = offset + 1 + count

                result = wos.utils.query(c, search, count=count, offset=offset)

                tree = ET.fromstring(result)

                for r in tree.findall('.//records'):
                    all_results.append(r)

                    if len(all_results) == self.n:

                        return all_results

    def process_results(self, results):
        all_dicts = []

        with tqdm.tqdm(total=len(results)) as pbar:
            for r in results:
                title = r.find('title/value').text

                keywords = [i.text for i in r.findall('keywords/value')]

                pub_info = {k:v for k, v in
                            zip([i.text for i in r.findall('source/label')], [i.text for i in r.findall('source/value')])}

                authors = [i.text for i in r.findall('authors/value')]

                other = {}
                o_pairs = r.findall('other')
                for o in o_pairs:
                    label = o.find('label').text
                    values = [i.text for i in o.findall('value')]
                    if len(values) == 1:
                        values = values[0]
                    other[label] = values

                pbar.update(1)

                r_dict = {'title':title,
                          'keywords':keywords,
                          'authors':authors,
                          }

                r_dict.update(pub_info)

                r_dict.update(other)

                all_dicts.append(r_dict)

        return all_dicts


class Scopus(Query):
    def __init__(self, label: str, search_phrase: str, date_range: tuple, results_dir: str, results_file: str, max_results: int):
        super().__init__(label, search_phrase, date_range, results_dir, results_file, max_results)
        self.original_search_phrase = search_phrase
        self.search_phrase = f"TITLE-ABS-KEY({search_phrase})"

        self.source = 'Scopus'
        self.data['metadata']['source'] = 'Scopus'

    def search(self):
        if all([self.start_date, self.end_date]):
            year_search_phrase = f"TITLE-ABS-KEY({self.original_search_phrase}) AND PUBYEAR > {self.start_date} AND PUBYEAR < {self.end_date}"
            results = pb.scopus.ScopusSearch(query=year_search_phrase)
        else:
            results = pb.scopus.ScopusSearch(query=self.search_phrase)

        if results:
            return results.results
        else:
            raise Exception("No results were returned.")

    def process_results(self, results, n=500):
        all_dicts = []

        if len(results) < n:
            n = len(results)

        with tqdm.tqdm(total=n) as pbar:
            for e, r in enumerate(results, 1):
                r_dict = dict(r._asdict())

                if r_dict.get('doi'):
                    r_dict['url'] = f"http://dx.doi.org/{r_dict['doi']}"
                    r_dict['saved_pdf_name'] = r_dict['doi'].replace('/', '_') + '.pdf'
                else:
                    r_dict['url'] = None
                    r_dict['saved_pdf_name'] = 'None.pdf'

                all_dicts.append(r_dict)

                pbar.update(1)

                if e == n:
                    break

        return all_dicts


class PubMed(Query):
    def __init__(self, label: str, search_phrase: str, date_range: tuple, results_dir: str, results_file: str, max_results: int):
        super().__init__(label, search_phrase, date_range, results_dir, results_file, max_results)
        self.search_phrase = search_phrase

        self.source = 'PubMed'
        self.data['metadata']['source'] = 'PubMed'

    def search(self):
        pubmed = pymed.PubMed(tool='SEBI', email='alexander.robertson@ed.ac.uk')

        if all([self.start_date, self.end_date]):
            year_search_phrase = f'{self.search_phrase} AND ("{self.start_date}"[Date - Publication] : "{self.end_date}"[Date - Publication])'

            results = pubmed.query(year_search_phrase, max_results=500)
        else:
            results = pubmed.query(self.search_phrase, max_results=500)

        return [r.toDict() for r in results]

    def process_results(self, results, n=500):
        all_dicts = []

        if len(results) < n:
            n = len(results)

        with tqdm.tqdm(total=n) as pbar:
            for e, r_dict in enumerate(results, 1):
                if r_dict.get('xml'):
                    del r_dict['xml']

                if r_dict['doi']:
                    r_dict['url'] = f"http://dx.doi.org/{r_dict['doi']}"
                    r_dict['saved_pdf_name'] = r_dict['doi'].replace('/', '_') + '.pdf'
                else:
                    r_dict['url'] = "http://dx.doi.org/None"
                    r_dict['saved_pdf_name'] = 'None.pdf'

                if r_dict.get('publication_date'):
                    r_dict['publication_date'] = str(r_dict['publication_date'])

                all_dicts.append(r_dict)

                pbar.update(1)

                if e == n:
                    break

        return all_dicts

