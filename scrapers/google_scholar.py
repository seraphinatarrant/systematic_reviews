from .search import Query

import os
import json
import tqdm
import scholarly


class GoogleScholar(Query):
    def __init__(self, label: string, search_phrase: string, date_range: tuple):
        super().__init__(label, search_phrase, date_range)

    def search(self):
        return scholarly.search_pubs_query(self.search_phrase)

    def search_with_year(self):
        custom_url = f"/scholar?q={self.search_phrase}&hl=en&as_sdt=0%2C5&as_ylo={self.start}&as_yhi={self.end}"
        return scholarly.search_pubs_custom_url(custom_url)

    def parse_results(self, query_results, log_folder, log=True, n=500):
        with tqdm.tqdm(total=n) as pbar:
            for e, r in enumerate(query_results, 1):
                try:
                    r.fill()
                except:
                    # Probably a 403 error on accessing the Bibtex URL
                    # Should make this more specific.
                    pass

                r_dict = r.__dict__

                if type(r_dict['bib']['abstract']) != str:
                    r_dict['bib']['abstract'] = r_dict['bib']['abstract'].text

                if r_dict['bib'].get('eprint'):
                    url = r_dict['bib']['eprint']

                if log:
                    os.makedirs(log_folder, exist_ok=True)

                    with open(f"{log_folder}/{self.label}", 'a') as o:
                        json.dump(r_dict, o, indent=5)
                        o.write('\n')
                        pbar.update(1)
        return r_dict

