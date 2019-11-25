import requests
from bs4 import BeautifulSoup
import json
import os

class Grabber:
    def __init__(self, url: str, save_location, bib_info: dict, label: str):
        self.save_location = save_location
        self.url = url
        self.bib_info = bib_info
        self.label = label

        self.grabber = self.choose_grabber()

    def choose_grabber(self):
        if "biomedcentral.com/" in self.url:
            return BiomedcentralGrabber(self.save_location, self.bib_info, self.label, self.url)
        if "springer.com/" in self.url:
            return SpringerGrabber(self.save_location, self.bib_info, self.label, self.url)
        if "sciencedirect.com/" in self.url:
            return ScienceDirectGrabber(self.save_location, self.bib_info, self.label, self.url)
        if "academia.edu/" in self.url:
            return AcademiaEduGrabber(self.save_location, self.bib_info, self.label, self.url)
        if "wiley.com/" in self.url:
            return WileyGrabber(self.save_location, self.bib_info, self.label, self.url)
        if "ncbi.nlm.nih.gov/" in self.url:
            return NIHGrabber(self.save_location, self.bib_info, self.label, self.url)
        if 'scielo.org.za/' in self.url:
            return ScieloGrabber(self.save_location, self.bib_info, self.label, self.url)

        return BaseGrabber(self.save_location, self.bib_info, self.label, self.url)

    def run(self, filename):
        pdf_data = self.grabber.get_pdf()
        self.grabber.write_pdf(pdf_data, filename)


class BaseGrabber:
    """
    Many sites won't allow access without a properly specified User-Agent in the header
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        self.save_location = save_location
        self.bib_info = bib_info
        self.label = label
        self.url = url

        os.makedirs(save_location, exist_ok=True)

    def get_pdf(self):
        url = self.fix_url()

        user_agent = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.5) Gecko/20091123 Iceweasel/3.5.5 (like Firefox/3.5.5; Debian-3.5.5-1)"
        headers = {'User-Agent': user_agent}

        r = requests.get(url, headers=headers, allow_redirects=True)

        if 'pdf' in r.headers.get('content-type').lower():
            return r.content
        else:
            return None

    def write_pdf(self, pdf_data: bytes, filename: str):
        if pdf_data:
            with open(f'{self.save_location}/{filename}', 'wb') as out:
                out.write(pdf_data)
        else:
            self.log()

    def fix_url(self):
        return self.url

    def log(self):
        os.makedirs('logs', exist_ok=True)

        with open(f'logs/failed_to_grab_{self.label}.txt', 'a') as out:
            out.write('\n')
            json.dump(self.bib_info, out)
            out.write('\n')
            out.write('='*70)

        print(f'Failed to get PDF: {self.url}')


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
        data = requests.get(self.url)
        html = BeautifulSoup(data.content, 'lxml')
        meta = html.find('meta', attrs={"name":'citation_pdf_url'})

        return meta.attrs['content']


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
        url = self.fix_url(self.url)

        user_agent = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.5) Gecko/20091123 Iceweasel/3.5.5 (like Firefox/3.5.5; Debian-3.5.5-1)"
        referer = "https://scholar.google.co.uk/scholar?hl=en&as_sdt=0%2C5&q=academic+paper&btnG="
        headers = {'User-Agent': user_agent, 'referer': referer}

        r = requests.get(url, headers=headers, allow_redirects=True)

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
        user_agent = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.5) Gecko/20091123 Iceweasel/3.5.5 (like Firefox/3.5.5; Debian-3.5.5-1)"
        headers = {'User-Agent': user_agent}
        data = requests.get(self.url, headers=headers)

        html = BeautifulSoup(data.content, 'lxml')
        meta = html.find('meta', attrs={"name":'citation_pdf_url'})

        new_url = meta.attrs['content']

        return new_url.replace('/doi/pdf/', '/doi/pdfdirect/')

class NIHGrabber(BaseGrabber):
    """
    Base URL needs fixed to point to PDF.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self):
        user_agent = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.5) Gecko/20091123 Iceweasel/3.5.5 (like Firefox/3.5.5; Debian-3.5.5-1)"
        headers = {'User-Agent': user_agent}
        data = requests.get(self.url, headers=headers)

        html = BeautifulSoup(data.content, 'lxml')

        meta = html.find('link', attrs={"type":'application/pdf'})

        return f"https://www.ncbi.nlm.nih.gov/{meta.attrs['href']}"

class ScieloGrabber(BaseGrabber):
    """
    The HTML has a well-defined link to the PDF's direct url.
    """
    def __init__(self, save_location: str, bib_info: dict, label: str, url: str):
        super().__init__(save_location, bib_info, label, url)

    def fix_url(self,):
        user_agent = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.5) Gecko/20091123 Iceweasel/3.5.5 (like Firefox/3.5.5; Debian-3.5.5-1)"
        headers = {'User-Agent': user_agent}
        data = requests.get(self.url, headers=headers)

        html = BeautifulSoup(data.content, 'lxml')

        meta = html.find('meta', attrs={"name": 'citation_pdf_url'})

        return meta.attrs['content']