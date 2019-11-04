# Individual scrapers for sources

## /

* `search_phrases.csv` : label/query pairs as defined by Dora. Can't find the Word document but can be seen in this Excel sheet: https://uoe-my.sharepoint.com/:x:/r/personal/cskeldon_ed_ac_uk/_layouts/15/Doc.aspx?sourcedoc={e3376c22-13f1-41b0-81dc-53b5d49d3792}&action=view&activeCell=%27Google%20Scholar%27!A2&wdInitialSession=778ab9c7-4994-4c50-88e4-d095c01658a2&wdRldC=1


## google_scholar/


* `query.py` : Basic scraper for Google Scholar. Super slow (~40 minutes to get 500 results for a single query), as want to avoid rate limiting - Google will block your IP for 24 hours. 
* `run_queries.sh` : Basic shell script to run a query/queries, for testing. Will change this in future to pull in `search_phrases.csv`