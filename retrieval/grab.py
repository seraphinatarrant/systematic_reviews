import os
import re
import json
import tqdm
import requests

from pathlib import Path
from bs4 import BeautifulSoup


def download(searcher, output_folder):
    """
    :param searcher: a search.Query object which has had its .run() method called.
    :param output_folder: location to save the PDFs to
    :return: None

    Wrapper for grab.GrabAll class, which itself just iteratively calls grab.GrabOne.
    """
    if searcher.data['results']:
        g = GrabAll(searcher, output_folder)
        g.run()


class GrabAll:
    def __init__(self, searcher, output_folder):
        self.searcher = searcher

        self.output_folder = Path(output_folder).expanduser()

    def run(self):

        main_bar = tqdm.tqdm(total=len(self.searcher.data['results']), desc='')

        for result in self.searcher.data['results']:
            
            g = GrabOne(save_location=self.output_folder,
                        bib_info=result,
                        label=self.searcher.label,
                        url=result['url'])

            main_bar.set_description_str(f"File: {result['saved_pdf_name']}")

            g.run(filename=result['saved_pdf_name'])

            main_bar.update(1)


class GrabOne:
    def __init__(self, save_location, bib_info: dict, label: str, url: str):
        self.save_location = Path(save_location).expanduser()
        self.label = label
        self.bib_info = bib_info

        if 'dx.doi.org/' in url:
            # Do the DOI redirect here to get the actual URL before choosing a Grabber
            self.url = self.resolve_doi(url)
        else:
            self.url = url

        self.grabber = self.choose_grabber()


    def resolve_doi(self, doi):
            user_agent = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.5) Gecko/20091123 Iceweasel/3.5.5 (like ' \
                         'Firefox/3.5.5; Debian-3.5.5-1) '
            headers = {'User-Agent': user_agent}

            if doi == 'http://dx.doi.org/None':
                self.log(reason=f'No DOI or URL was available for this item')
                return "http://none"

            try:
                r = requests.get(doi, headers=headers, allow_redirects=True, timeout=(10,10))
            except Exception as e:
                self.log(reason=f'Exception raised for DOI {doi} : {e}')
                return "http://none"

            if r.status_code != 200:
                self.log(reason=f'HTTP Error for DOI {doi} : {r.status_code}')
                return "http://none"

            if 'elsevier.com/' in r.url:
                target = r.url.split('/')[-1]
                return f"https://www.sciencedirect.com/science/article/pii/{target}"

            return r.url

    def log(self, reason=None):
        os.makedirs(f'{self.save_location}/logs', exist_ok=True)

        self.bib_info['DOI_fail_reason'] = reason

        with open(f'{self.save_location}/logs/failed_to_resolve_DOI_{self.label}.txt', 'a') as out:
            out.write('\n')
            json.dump(self.bib_info, out)
            out.write(f'\n')
            out.write('='*70)

    def choose_grabber(self):
        args = dict(save_location=self.save_location,
                    bib_info=self.bib_info,
                    label=self.label,
                    url=self.url)

        if self.url.lower() == "http://none":
            return NoURL(**args)

        try:
            data = requests.get(self.url, timeout=(10,10))
        except:
            return NoURL(**args)

        html = BeautifulSoup(data.content, 'lxml')
        meta = html.find('meta', attrs={"name":'citation_pdf_url'})

        if meta:
            args['url'] = meta.attrs['content']
            return CitationPDFURL(**args)

        if "biomedcentral.com/" in self.url:
            return BiomedcentralGrabber(**args)
        if "springer.com/" in self.url:
            return SpringerGrabber(**args)
        if "sciencedirect.com/" in self.url:
            return ScienceDirectGrabber(**args)
        if "academia.edu/" in self.url:
            return AcademiaEduGrabber(**args)
        if "wiley.com/" in self.url:
            return WileyGrabber(**args)
        if "ncbi.nlm.nih.gov/" in self.url:
            return NIHGrabber(**args)
        if 'scielo.org.za/' in self.url:
            return ScieloGrabber(**args)
        if 'journals.plos.org/' in self.url:
            return PlosGrabber(**args)
        if 'ojvr.org/' in self.url:
            return OJVRGrabber(**args)
        if 'cambridge.org/' in self.url:
            return CambridgeGrabber(**args)
        if 'veterinaryworld.org/' in self.url:
            return VetWorldGrabber(**args)
        if 'hindawi.com/' in self.url:
            return HindawiGrabber(**args)
        if 'ejmanager' in self.url:
            return EJManagerGrabber(**args)
        if 'scialert.net/' in self.url:
            return SciAlertGrabber(**args)
        if 'medwelljournals.' in self.url:
            return MedwellGrabber(**args)
        if 'jidc.org/' in self.url:
            return JIDCGrabber(**args)
        if 'oup.com/' in self.url:
            return OUPGrabber(**args)
        if 'aem.asm.org/' in self.url:
            return ASMAEMGrabber(**args)
        if 'frontiersin.org/' in self.url:
            return FrontiersGrabber(**args)
        if 'indianjournals.com/' in self.url:
            return IndianJournalsGrabber(**args)
        if 'springeropen.com/' in self.url:
            return SpringerOpenGrabber(**args)
        if 'tandfonline.com/' in self.url:
            return TandFGrabber(**args)
        if 'ijpsr.com/' in self.url:
            return IJPSRGrabber(**args)
        if 'liebertpub.com/' in self.url:
            return LiebertGrabber(**args)
        if 'ajtmh.org/' in self.url:
            return AJTMHGrabber(**args)
        if 'panafrican-med-journal' in self.url:
            return PanAfricanGrabber(**args)
        if 'sagepub.com/' in self.url:
            return SagePubGrabber(**args)
        if 'akademia.com/' in self.url:
            return AkademiaiGrabber(**args)
        if 'ajol.info/' in self.url:
            return AJOLGrabber(**args)
        if 'jfoodprotection.org/' in self.url:
            return JFoodGrabber(**args)
        if 'jsava.co.za/' in self.url:
            return JsavaGrabber(**args)
        if 'bioone.org/' in self.url:
            return BiooneGrabber(**args)
        if 'humankinetics.com/' in self.url:
            return HumanKineticsGrabber(**args)
        if 'cdc.gov/' in self.url:
            return CDCGrabber(**args)
        if 'ekb.eg/' in self.url:
            return EKBGrabber(**args)
        if 'microbiologyresearch.org/' in self.url:
            return MicroBioResearch(**args)

        return BaseGrabber(**args)

    def run(self, filename):
        if hasattr(self, 'grabber'):

            if self.url == 'http://none':
                self.grabber.log(reason=f'Could not resolve DOI to URL. Error: {self.grabber.error}')
            else:

                pdf_data = self.grabber.get_pdf()

                self.grabber.write_pdf(pdf_data, filename)
                self.grabber.write_json(self.grabber.bib_info, filename)


class BaseGrabber:
    """
    Many sites won't allow access without a properly specified User-Agent in the header
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        self.save_location = save_location
        self.bib_info = bib_info
        self.label = label
        self.url = url
        self.error = 'None'
        self.original_url = url

        os.makedirs(save_location, exist_ok=True)

    def get_pdf(self):
        url = self.fix_url()

        user_agent = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.5) Gecko/20091123 Iceweasel/3.5.5 (like " \
                     "Firefox/3.5.5; Debian-3.5.5-1) "
        headers = {'User-Agent': user_agent}

        try:
            r = requests.get(url, headers=headers, allow_redirects=True, timeout=(10, 10))
        except Exception as e:
            self.log(reason=f'Could not get PDF. Exception: {e}')
            return None

        if r.status_code != 200:
            self.log(reason=f'Could not access PDF URL. HTTP Error: {r.status_code} ({r.reason}')
            return None

        if 'pdf' in r.headers.get('content-type').lower():
            return r.content
        else:
            self.log(reason=f'No PDF content at URL. HTTP Error: {r.status_code} ({r.reason}')
            return None

    def write_pdf(self, pdf_data: bytes, filename: str):
        if pdf_data:
            try:
                with open(f'{self.save_location}/{filename}', 'wb') as out:
                    out.write(pdf_data)
            except Exception as e:
                self.log(reason=f'Could not write data to PDF. Error: {e}')
        else:
            self.log(reason='No PDF data found.')

    def write_json(self, json_data: dict, filename: str):
        with open(f"{self.save_location}/{filename.replace('.pdf', '.json')}", 'w') as f:
            json.dump(json_data, f, indent=5)

    def fix_url(self):
        return self.url

    def log(self, reason=None):
        os.makedirs(f'{self.save_location}/logs', exist_ok=True)

        self.bib_info['Reason_for_failure'] = reason

        with open(f'{self.save_location}/logs/failed_to_get_PDF_{self.label}.txt', 'a') as out:
            out.write('\n')
            json.dump(self.bib_info, out)
            out.write(f'\n')
            out.write('='*70)

class NoURL(BaseGrabber):
    """
    Dummy class for results with no URL
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def run(self, filename):
        self.log(reason=f'No DOI was available from search result.')


class CitationPDFURL(BaseGrabber):
    """
    Link to PDF is in metadata
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        return self.url


class PanAfricanGrabber(BaseGrabber):
    """
    Link to article needs URL changed to point to PDF.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        fname = self.url.split('/')[-2]

        new_url = self.url.replace('/full/', '/pdf/')

        return f"{new_url}{fname}.pdf"


class LiebertGrabber(BaseGrabber):
    """
    Link to article needs URL changed to point to PDF.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        new_url = self.url.replace('/doi/', '/doi/pdf/')

        return new_url


class JFoodGrabber(BaseGrabber):
    """
    Link to article needs URL changed to point to PDF.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        new_url = self.url.replace('/doi/', '/doi/pdf/')

        return new_url


class AkademiaiGrabber(BaseGrabber):
    """
    Link to article needs URL changed to point to PDF.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        new_url = self.url.replace('/doi/', '/doi/pdf/')

        return new_url


class SagePubGrabber(BaseGrabber):
    """
    Link to article needs URL changed to point to PDF.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        new_url = self.url.replace('/doi/', '/doi/pdf/')

        return new_url


class IJPSRGrabber(BaseGrabber):
    """
    Parse HTML and get PDF link
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            a_tag = [i for i in html.find_all('a') if i.get('href').endswith('.pdf')][0]

            return a_tag.get('href')
        except:
            return self.url


class MedwellGrabber(BaseGrabber):
    """
    Parse HTML and get PDF link
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        data = requests.get(self.url, timeout=(10,10))
        html = BeautifulSoup(data.content, 'lxml')
        a_tag = html.find('a', string='Fulltext PDF')

        if a_tag:
            return a_tag.get('href')
        else:
            return self.url


class AJTMHGrabber(BaseGrabber):
    """
    Parse HTML and get PDF link
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            link = html.find("a", attrs={'class': "pdf"})
            
            return f"https://www.ajtmh.org{link.get('href')}"

        except:
            return self.url


class TandFGrabber(BaseGrabber):
    """
    Parse HTML and get PDF link
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            link = html.find("a", attrs={'class': "show-pdf"})

            return f"https://www.tandfonline.com{link.get('href')}"

        except:
            return self.url


class EKBGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']

        except:
            return self.url

class CDCGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']

        except:
            return self.url


class HumanKineticsGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']

        except:
            return self.url


class BiooneGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']

        except:
            return self.url


class JsavaGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']

        except:
            return self.url


class AJOLGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']
        except:
            return self.url


class SpringerOpenGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']
        except:
            return self.url


class IndianJournalsGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']
        except:
            return self.url


class FrontiersGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']
        except:
            return self.url


class HindawiGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']
        except:
            return self.url


class ASMAEMGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']
        except:
            return self.url


class OUPGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']
        except:
            return self.url


class JIDCGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']
        except:
            return self.url


class SciAlertGrabber(BaseGrabber):
    """
    Link to article needs URL changed to point to PDF.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        new_url = self.url.replace('/abstract/', '/qredirect.php')

        return f"{new_url}&linkid=pdf"


class EJManagerGrabber(BaseGrabber):
    """
    Extract window.location from Javascript redirect.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            # html = BeautifulSoup(data.content, 'lxml')
            redirmatch = re.match(r'.*?window\.location\s*=\s*\"([^"]+)\"', str(data.content), re.M|re.S)

            if redirmatch and "http" in redirmatch.group(1):
                new_url = redirmatch.group(1)
                return new_url
            else:
                return self.url
        except:
            return self.url


class OJVRGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name":'citation_pdf_url'})

            return meta.attrs['content']
        except:
            return self.url


class CambridgeGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name":'citation_pdf_url'})

            return meta.attrs['content']
        except:
            return self.url


class PlosGrabber(BaseGrabber):
    """
    Link to article needs URL changed to point to PDF.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        new_url = self.url.replace('/article?', '/article/file?')
        return f"{new_url}&type=printable"


class VetWorldGrabber(BaseGrabber):
    """
    Link to article needs URL changed to point to PDF.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        return self.url.replace('.html', '.pdf')


class BiomedcentralGrabber(BaseGrabber):
    """
    Link to article needs URL changed to point to PDF.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        return self.url.replace('/articles/', '/track/pdf/')


class SpringerGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        try:
            data = requests.get(self.url, timeout=(10,10))
            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']
        except:
            return self.url


class ScienceDirectGrabber(BaseGrabber):
    """
    Need to append parameter to the URL to avoid JavaScript mess
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self,):
        return self.url + "/pdfft?isDTMRedir=true&download=true"


class AcademiaEduGrabber(BaseGrabber):
    """
    Will only let you get the PDF if you are coming from Google.
    Spoof a Google Scholar referer.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def get_pdf(self):
        user_agent = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.5) Gecko/20091123 Iceweasel/3.5.5 (like " \
                     "Firefox/3.5.5; Debian-3.5.5-1) "
        referer = "https://scholar.google.co.uk/scholar?hl=en&as_sdt=0%2C5&q=academic+paper&btnG="
        headers = {'User-Agent': user_agent, 'referer': referer}

        try:
            r = requests.get(self.url, headers=headers, allow_redirects=True, timeout=(10,10))
        except :
            print(f'Error: {self.url}')
            return None

        if 'pdf' in r.headers.get('content-type').lower():
            return r.content
        else:
            return None


class WileyGrabber(BaseGrabber):
    """
    Need to specify User-Agent.
    Will try to render PDF using JavaScript via ReadCube.com, so change URL to go direct to PDF.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        user_agent = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.5) Gecko/20091123 Iceweasel/3.5.5 (like " \
                     "Firefox/3.5.5; Debian-3.5.5-1) "
        headers = {'User-Agent': user_agent}

        try:
            data = requests.get(self.url, headers=headers, timeout=(10,10))

            html = BeautifulSoup(data.content, 'lxml')
            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            new_url = meta.attrs['content']

            return new_url.replace('/doi/pdf/', '/doi/pdfdirect/')

        except:
            return self.url


class NIHGrabber(BaseGrabber):
    """
    Base URL needs fixed to point to PDF.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        user_agent = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.5) Gecko/20091123 Iceweasel/3.5.5 (like " \
                     "Firefox/3.5.5; Debian-3.5.5-1) "
        headers = {'User-Agent': user_agent}

        try:
            data = requests.get(self.url, headers=headers, timeout=(10,10))

            html = BeautifulSoup(data.content, 'lxml')

            meta = html.find('link', attrs={"type": 'application/pdf'})

            return f"https://www.ncbi.nlm.nih.gov/{meta.attrs['href']}"

        except:
            return self.url


class ScieloGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self,):
        user_agent = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.5) Gecko/20091123 Iceweasel/3.5.5 (like " \
                     "Firefox/3.5.5; Debian-3.5.5-1) "
        headers = {'User-Agent': user_agent}

        try:
            data = requests.get(self.url, headers=headers, timeout=(10,10))

            html = BeautifulSoup(data.content, 'lxml')

            meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

            return meta.attrs['content']

        except:
            return self.url


class MicroBioResearch(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self,):
        user_agent = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.5) Gecko/20091123 Iceweasel/3.5.5 (like " \
                     "Firefox/3.5.5; Debian-3.5.5-1) "
        headers = {'User-Agent': user_agent}

        try:
            data = requests.get(self.url, headers=headers, timeout=(10,10))

            html = BeautifulSoup(data.content, 'lxml')

            meta = html.find('div', attrs={"class":"ft-download-content ft-download-content--pdf"})

            url = meta.find('form').attrs['action']

            return  "https://www.microbiologyresearch.org" + url

        except:
            return self.url
