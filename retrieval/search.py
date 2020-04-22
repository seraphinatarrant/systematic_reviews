import json
import tqdm
import datetime
import requests
import hashlib
import argparse

from .grab import download

from pathlib import Path
from xml.etree import ElementTree as ET

from serpapi.google_scholar_search_results import GoogleScholarSearchResults  # Google Scholar

with open('/home/alexander/Dropbox/sebi_information_retrieval/retrieval/serpapi_key.txt') as f:
    # Load the API key for serpapi
    GoogleScholarSearchResults.SERP_API_KEY = f.read().strip()

import pybliometrics as pb  # Scopus
import wos  # Web of Knowledge
import pymed  # PubMed


def query_and_run(source: str, label: str, search_phrase: str, date_range: tuple, results_file: str, max_results: int):
    """
    :param source: search engine to query (google, wos, scopus, pubmed)
    :param label: a reference label for this query (e.g. brucellosis_sheep_nigeria)
    :param search_phrase: the actual search query. This should match the syntax of the source you are using!
    :param date_range: Restrict results to (start_year, end_year), e.g. (2012, 2018)
    :param results_file: Name of the json file to save all results in
    :param max_results: Maximum number of results you want.
    :return: Query object

    Returns the Query object, which is then passed to grab.GrabAll class to download the PDFs of the results.
    """


    all_sources = {'google': GoogleScholar, 'wos': WoS, 'scopus': Scopus, 'pubmed': PubMed}

    selection = all_sources[source]

    searcher = selection(label=label,
                         search_phrase=search_phrase,
                         date_range=date_range,
                         results_file=results_file,
                         max_results=max_results)

    searcher.run()

    return searcher


class Query:
    def __init__(self, label: str, search_phrase: str, date_range: tuple, results_file: str, max_results: int):
        self.label = label

        self.search_phrase = search_phrase

        self.start_date, self.end_date = date_range

        self.results_file = Path(results_file).expanduser()

        self.max_results = max_results

        self.processed_results = None

        self.source = None

        self.data = {'metadata': {'source': self.source,
                                  'label': self.label,
                                  'search_phrase': self.search_phrase,
                                  'date_range': [self.start_date, self.end_date],
                                  'query_datetime': datetime.datetime.now().strftime("%d-%b-%Y_%H:%M:%S"),
                                  'max_results': self.max_results,
                                  },
                     'results': None
                     }

    def search(self):
        raise NotImplementedError

    def process_results(self, search_results):
        raise NotImplementedError

    def save_to_json(self):
        print(f"Saving results to: {self.results_file}")

        if self.results_file.parent.parts:
            self.results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.results_file, 'w') as o:
            json.dump(self.data, o, indent=5)

        print(f"Done!")

    def run(self):
        self.search_results = self.search()

        if self.search_results:
            self.data['results'] = self.process_results(self.search_results)
        else:
            self.data['results'] = None
            print('No results found...')

        self.save_to_json()


class GoogleScholar(Query):
    def __init__(self, label: str, search_phrase: str, date_range: tuple, results_file: str, max_results: int):
        super().__init__(label, search_phrase, date_range, results_file, max_results)

        self.source = 'Google_Scholar'
        self.data['metadata']['source'] = 'Google_Scholar'

    def search(self):
        params = {"q": self.search_phrase,
                  "hl": "en"
                  }

        if all([self.start_date, self.end_date]):
            params["as_ylo"] = self.start_date
            params["as_yhi"] = self.end_date

        client = GoogleScholarSearchResults(params)

        results = client.get_dict()

        if results.get('error'):
            return

        if int(results['search_information']['total_results']) < self.max_results:
            new_max = int(results['search_information']['total_results'])
        else:
            new_max = self.max_results

        all_results = [i for i in results['organic_results']]

        for i in all_results:
            if i.get('link', None):
                i['url'] = i['link']
                i['saved_pdf_name'] = hashlib.md5(i['link'].encode()).hexdigest() + '.pdf'
            else:
                i['url'] = "http://none"
                i['saved_pdf_name'] = hashlib.md5(i['title'].encode()).hexdigest() + '.pdf'

        if results['search_information']['total_results'] <= self.max_results:
            return all_results

        while len(all_results) < new_max:
            if results.get('serpapi_pagination'):
                pass
            else:
                return all_results

            results = requests.get(results['serpapi_pagination']['next_link'])

            results = json.loads(results.content)

            for i in results['organic_results']:
                if i.get('link', None):
                    i['url'] = i['link']
                    i['saved_pdf_name'] = hashlib.md5(i['link'].encode()).hexdigest() + '.pdf'
                else:
                    i['url'] = "http://none"
                    i['saved_pdf_name'] = hashlib.md5(i['title'].encode()).hexdigest() + '.pdf'

                all_results.append(i)

                if len(all_results) == new_max:
                    break

        return all_results

    def process_results(self, search_results):

        with tqdm.tqdm(total=len(search_results)) as pbar:
            for i in search_results:
                pbar.update(1)

        return search_results


class WoS(Query):
    def __init__(self, label: str, search_phrase: str, date_range: tuple, results_file: str, max_results: int):
        super().__init__(label, search_phrase, date_range, results_file, max_results)
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

        if self.max_results < count:
            count = self.max_results

        all_results = []

        with client as c:
            result = wos.utils.query(c, self.search_phrase, count=count, offset=offset)

            tree = ET.fromstring(result)

            max_total = int(tree.find('recordsFound').text)

            print(f"Total matches found: {max_total}")

            for r in tree.findall('.//records'):
                if len(all_results) == self.max_results:
                    break
                else:
                    all_results.append(r)

            loops = round(max_total / count)

            if loops in {0, 1}:
                # We only needed one loop, so have got all we can, so return it.
                print(f'\tTotal papers grabbed: {len(all_results)}')
                return all_results

            for loop in range(loops - 1):
                offset = offset + 1 + count

                result = wos.utils.query(c, self.search_phrase, count=count, offset=offset)

                tree = ET.fromstring(result)

                for r in tree.findall('.//records'):
                    all_results.append(r)

                    if len(all_results) == self.max_results:
                        return all_results

    def process_results(self, results):
        all_dicts = []

        with tqdm.tqdm(total=len(results)) as pbar:
            for r in results:
                title = r.find('title/value').text

                keywords = [i.text for i in r.findall('keywords/value')]

                pub_info = {k: v for k, v in
                            zip([i.text for i in r.findall('source/label')],
                                [i.text for i in r.findall('source/value')])}

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

                r_dict = {'title': title,
                          'keywords': keywords,
                          'authors': authors,
                          }

                r_dict.update(pub_info)

                r_dict.update(other)

                r_dict['url'] = "http://none"
                r_dict['saved_pdf_name'] = "None"

                if r_dict.get('Identifier.Doi', None):
                    r_dict['url'] = f"http://dx.doi.org/{r_dict['Identifier.Doi']}"
                    r_dict['saved_pdf_name'] = r_dict['Identifier.Doi'].replace('/', '_') + '.pdf'
                else:
                    if r_dict.get('Identifier.Xref_Doi', None):
                        r_dict['url'] = f"http://dx.doi.org/{r_dict['Identifier.Xref_Doi']}"
                        r_dict['saved_pdf_name'] = r_dict['Identifier.Xref_Doi'].replace('/', '_') + '.pdf'


                all_dicts.append(r_dict)

        return all_dicts


class Scopus(Query):
    def __init__(self, label: str, search_phrase: str, date_range: tuple, results_file: str, max_results: int):
        super().__init__(label, search_phrase, date_range, results_file, max_results)
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

    def process_results(self, results):
        all_dicts = []

        if len(results) < self.max_results:
            n = len(results)
        else:
            n = self.max_results

        with tqdm.tqdm(total=len(results)) as pbar:
            for e, r in enumerate(results, 1):
                r_dict = dict(r._asdict())

                if r_dict.get('doi'):
                    r_dict['url'] = f"http://dx.doi.org/{r_dict['doi']}"
                    r_dict['saved_pdf_name'] = r_dict['doi'].replace('/', '_') + '.pdf'
                else:
                    r_dict['url'] = "http://none"
                    r_dict['saved_pdf_name'] = 'None.pdf'

                all_dicts.append(r_dict)

                pbar.update(1)

                if e == n:
                    break

        return all_dicts


class PubMed(Query):
    def __init__(self, label: str, search_phrase: str, date_range: tuple, results_file: str, max_results: int):
        super().__init__(label, search_phrase, date_range, results_file, max_results)
        self.search_phrase = search_phrase

        self.source = 'PubMed'
        self.data['metadata']['source'] = 'PubMed'

    def search(self):
        pubmed = pymed.PubMed(tool='SEBI', email='alexander.robertson@ed.ac.uk')

        if all([self.start_date, self.end_date]):
            year_search_phrase = f'{self.search_phrase} AND ("{self.start_date}"[Date - Publication] : "{self.end_date}"[Date - Publication])'

            results = pubmed.query(year_search_phrase, max_results=self.max_results)
        else:
            results = pubmed.query(self.search_phrase, max_results=self.max_results)

        return [r.toDict() for r in results]

    def process_results(self, results):
        all_dicts = []

        if len(results) < self.max_results:
            n = len(results)
        else:
            n = self.max_results

        with tqdm.tqdm(total=len(results)) as pbar:
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
