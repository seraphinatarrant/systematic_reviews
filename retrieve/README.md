# Individual scrapers for sources

## search_phrases.csv

* `search_phrases.csv` : label/query pairs as defined by Dora. Can't find the Word document but can be seen in this Excel sheet: `https://uoe-my.sharepoint.com/:x:/r/personal/cskeldon_ed_ac_uk/_layouts/15/Doc.aspx?sourcedoc={e3376c22-13f1-41b0-81dc-53b5d49d3792}&action=view&activeCell=%27Google%20Scholar%27!A2&wdInitialSession=778ab9c7-4994-4c50-88e4-d095c01658a2&wdRldC=1`


## search.py

Script to submit query to one of four search engines. Generates JSON for results and will also download all PDFs of results, where possible.

- source 	:  Search engine to use, choices=['google', 'wos', 'pubmed', 'scopus']
- output 	:  Filename for json output
- pdf_folder :  Path to save PDFs to
- max 		:  Max number of hits to return
- label 		:  Label for search query, such as disease. Used to name certain output files.
- search 	:  Search terms to us
- range 		:  default=[2015, 2020], Limit results to papers from these years, inclusive.

## grab.py

Code for downloading PDFs based on a search result.