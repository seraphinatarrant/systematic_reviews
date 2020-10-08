import re
import os
import sys
import glob
import json
import tqdm
import spacy
import argparse
import cleantext
import subprocess

from pathlib import Path


hyphenspace = re.compile(r'-\s')
nls = re.compile(r'(?<![\r\n])(\r?\n|\n?\r)(?![\r\n])')
spaces = re.compile(r'\s+')


nlp = spacy.load('en_core_web_sm')


def clean_text(text):
    """
    :param text: str
    :return: str

    Basic text cleaner for PDF-extracted content.
    """

    # Remove weird ligatures with spaces
    text = text.replace('ﬂ ', 'fl').replace('ﬁ ', 'fi').replace('ﬀ ', 'ff')

    clean = hyphenspace.sub('', text)
    # Remove word-internal linebreaks
    clean = hyphenspace.sub('', text)
    # Remove random newlines
    clean = nls.sub(' ', clean)
    # Remove multiple consecutive spaces
    clean = spaces.sub(' ', clean)

    # Other random stuff
    clean = cleantext.clean(clean, lower=False)

    return clean


def process_pdf_folder(source_folder, output_folder, extract=True):
    """
    :param source_folder: str
    :param output_folder: str - where to save the extracted full text (.txt) and paper sections (.json)
    :return: None

    Reads in all PDFs in a folder, converts to text, cleans it a bit, extracts sections, saves to JSON.

    """
    source_folder = Path(source_folder).expanduser()
    output_folder = Path(output_folder).expanduser()

    os.makedirs(f"{output_folder}/full_txt", exist_ok=True)
    os.makedirs(f"{output_folder}/sections_json", exist_ok=True)

    pdf_files = glob.glob(f"{source_folder}/*.pdf")

    pdf_bar = tqdm.tqdm(total=len(pdf_files), desc='{desc}', position=0)

    # Call pdfminer's script to extract all text from PDFs.
    # Automatically saved to output folder.
    if extract:
        for file in pdf_files:
            p = Path(file)
            new_name = p.stem + '.txt'

            pdf_bar.set_description_str(f'Converting PDF: {p.name}')

            try:
                #subprocess.check_output(['pdf2txt.py', '-o', f'{output_folder}/full_txt/{new_name}', file])
                subprocess.check_output(['python', 'C:\\Users\\Alexander\\Miniconda3\\envs\\sebi_information_retrieval\\Scripts\\pdf2txt.py', '-o', f'{output_folder}/full_txt/{new_name}', file])
            except:
                with open(f"{output_folder}/failed_to_extract.log", 'a') as log:
                    log.write(f'Could not extract text from: {file}\n')

            pdf_bar.update(1)

    tqdm.tqdm.write('Extracting sections from text files...')

    txt_files = glob.glob(f'{output_folder}/full_txt/*.txt')

    # Load the regular expressions for extracting sections
    with open('./extract/data/regex_dict.json', 'r') as f:
        chain_dict = json.load(f)

    all_best = {}

    main_bar = tqdm.tqdm(total=len(txt_files), desc='{desc}', position=1)

    # Clean the text and extract sections.
    for file in txt_files:
        p = Path(file)

        print(file)

        with open(file, encoding='utf8') as f:
            t = f.read()
            t = clean_text(t)

        main_bar.set_description_str(f'Extracting text: {p.name}')

        best_matches = {}

        for k in chain_dict:
            finds = False
            best = None

            for a in chain_dict[k]:
                m = re.search(a, t)
                if m:
                    finds = True

                    if best:
                        if m.span()[1] - m.span()[0] < best.span()[1] - best.span()[0]:
                            best = m
                    else:
                        best = m
            if best:
                best_matches[k] = best.group(k)

        main_bar.update(1)

        all_best[file] = best_matches

    json_bar = tqdm.tqdm(total=len(all_best), desc='{desc}', position=2)

    # Save the sections to JSON
    for full_path, sections in all_best.items():
        p = Path(full_path)
        new_name = p.stem + '.json'

        all_data = {'file': p.name, 'data': {}}

        json_bar.set_description_str(f'Saving to JSON: {p.name}')

        for section, text in sections.items():
            all_data['data'][section] = {'text': text}

            doc = nlp(text)

            sentences = [s.text for s in doc.sents]

            all_data['data'][section]['sentences'] = sentences

        json_bar.update(1)

        with open(f"{output_folder}/sections_json/{new_name}", 'w') as f:
            json.dump(all_data, f, indent=5)


def combine_json_and_bibinfo(source_folder, bibinfo_folder):
    """
    :param source_folder:
    :param bibinfo_folder:
    :return: None

    Once process_pdf_folder() has created the section jsons, in source_folder, these are loaded along with the
    bibinfo folder jsons created during the search/grab phase.

    This function combines them so that later on it is easy to link extracted data to the actual source and use
    bibinfo to populate relevant fields like author, title.
    """
    source_jsons = sorted(glob.glob(f"{source_folder}/sections_json/*.json"))
    bibinfo_jsons = sorted(glob.glob(f"{bibinfo_folder}/*.json"))

    print(source_jsons)
    print(bibinfo_jsons)

    print(len(source_jsons), len(bibinfo_jsons))

    #assert len(source_jsons) == len(bibinfo_jsons)

    for source, bib in zip(source_jsons, bibinfo_jsons):
        with open(source) as f:
            source_j = json.load(f)
        with open(bib) as f:
            bib_j = json.load(f)

        source_j['bib_info'] = bib_j

        with open(source, 'w') as f:
            json.dump(source_j, f, indent=5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert PDF to text')
    parser.add_argument('source_folder', help='Location of PDFs')
    parser.add_argument('bibinfo_folder', help='Location of JSONs with bibinfo for PDFs')
    parser.add_argument('output_folder', help='Where to save the text files')

    args = parser.parse_args()

    process_pdf_folder(args.source_folder, args.output_folder)

    combine_json_and_bibinfo(args.output_folder, args.bibinfo_folder)
