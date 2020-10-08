from .grab import download
from .search import GoogleScholar, WoS, Scopus, PubMed

engines = {'google': GoogleScholar,
           'wos': WoS,
           'scopus': Scopus,
           'pubmed': PubMed}
