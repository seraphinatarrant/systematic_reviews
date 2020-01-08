"""As per API docs here: https://en.wikipedia.org/api/rest_v1/#/, limit to 200 req/sec"""
import sys
import requests
import json
from urllib import parse


API_BASE = "https://en.wikipedia.org/api/rest_v1/"
CITATION_BASE = "data/citation/"
FORMAT = "zotero/"


def make_query_url(identifier: str) -> str:
    query_url = API_BASE + CITATION_BASE + FORMAT + parse.quote_plus(identifier)
    return query_url

def get_citation_data(identifier: str) -> dict:
    """takes a url for a pdf, a doi, or issn, and returns citation data"""
    query_url = make_query_url(identifier)
    response = requests.get(query_url)
    if response.status_code == 200:
        return json.loads(response.text)[0] # for some reason it is nested in a list of length 1 TODO make sure never returns a multi-item list
    else:
        print("No data returned for url: {}, status code: {}".format(
            identifier, response.status_code), file=sys.stderr)
        return {}


if __name__ == "__main__":

    #For tests:
    TEST_URL = "https://www.cambridge.org/core/services/aop-cambridge-core/content/view/35DA0ACFED3E13EA7D7C2C6A69260664/S1742758400007475a.pdf/ticks_and_tickborne_parasites_associated_with_indigenous_cattle_in_didtuyura_ranch_southern_ethiopia.pdf"
    ENCODED_TEST_URL = "https://en.wikipedia.org/api/rest_v1/data/citation/zotero/https%3A%2F%2Fwww.cambridge.org%2Fcore%2Fservices%2Faop-cambridge-core%2Fcontent%2Fview%2F35DA0ACFED3E13EA7D7C2C6A69260664%2FS1742758400007475a.pdf%2Fticks_and_tickborne_parasites_associated_with_indigenous_cattle_in_didtuyura_ranch_southern_ethiopia.pdf"

    citation_data = get_citation_data(TEST_URL)
    print(len(citation_data))
