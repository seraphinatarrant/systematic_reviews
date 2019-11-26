import os
import json
import tqdm
import scholarly  # Google Scholar


class Query:
    def __init__(self, label: str, search_phrase: str, date_range: tuple, results_folder: str, max_results: int):
        self.label = label
        self.search_phrase = search_phrase
        self.start_date, self.end_date = date_range
        self.results_folder = results_folder
        self.n = max_results

        self.processed_results = None

    def search(self):
        raise NotImplementedError

    def search_with_year(self):
        raise NotImplementedError

    def process_results(self, search_results, save, n):
        raise NotImplementedError

    def run(self):
        search_results = self.search_with_year()

        self.processed_results = self.process_results(search_results, save=True, n=self.n)


class GoogleScholar(Query):
    def __init__(self, label: str, search_phrase: str, date_range: tuple, results_folder: str, max_results: int):
        super().__init__(label, search_phrase, date_range, results_folder, max_results)

    def search(self):
        return scholarly.search_pubs_query(self.search_phrase)

    def search_with_year(self):
        custom_url = f"/scholar?q={self.search_phrase}&hl=en&as_sdt=0%2C5&as_ylo={self.start_date}&as_yhi={self.end_date}"
        return scholarly.search_pubs_custom_url(custom_url)

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

        if save:
            print(f"Saving results to: {self.results_folder}/{self.label}.json")
            os.makedirs(self.results_folder, exist_ok=True)

            with open(f"{self.results_folder}/{self.label}.json", 'a') as o:
                json.dump(all_dicts, o, indent=5)
                o.write('\n')
        return all_dicts


