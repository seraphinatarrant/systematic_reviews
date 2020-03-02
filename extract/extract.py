import re
import glob
import json
import tqdm
import argparse
import subprocess

from pathlib import Path

hyphenspace = re.compile('-\s')
nls = re.compile('(?<![\r\n])(\r?\n|\n?\r)(?![\r\n])')
spaces = re.compile('\s+')

def clean_text(text):
    #Remove word-internal linebreaks
    clean = hyphenspace.sub('', text)
    #Remove random newlines
    clean = nls.sub(' ', clean)
    #Remove multiple consecutive spaces
    clean = spaces.sub(' ', clean)

    return clean

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert PDF to text')
    parser.add_argument('source_folder', help='Location of PDFs')
    parser.add_argument('output_folder', help='Where to save the text files')

    args = parser.parse_args()

    pdf_files = glob.glob(f"{args.source_folder}/*.pdf")

    pdf_bar = tqdm.tqdm(total=len(pdf_files), desc='{desc}', position=0)

    # Call pdfminer's script to extract all text from PDFs.
    # Automatically saved to output folder.
    for file in pdf_files:
        p = Path(file)

        pdf_bar.set_description_str(f'Converting PDF: {file}')

        subprocess.run(['pdf2txt.py', '-o', f'{args.output_folder}/{p.stem}.txt', file])

        pdf_bar.update(1)

    tqdm.tqdm.write('Extracting sections from text files...')

    txt_files = glob.glob( f'{args.output_folder}/*.txt')

    # Load the regular expressions for extracting sections
    with open('regex_dict.json', 'r') as f:
        chain_dict = json.load(f)

    all_best = {}

    main_bar = tqdm.tqdm(total=len(txt_files), desc='{desc}', position=1)

    # Clean the text and extract sections.
    for file in txt_files:
        with open(file) as f:
            t = f.read()
            t = clean_text(t)

        main_bar.set_description_str(f'Extracting text: {file}')

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

    # Save the sections to JSON
    for full_path, sections in all_best.items():
        p = Path(full_path)
        new_name = p.stem + '.json'

        all_data = {'file':p.name, 'data':{}}

        for section, text in sections.items():

            all_data['data'][section] = {'text': text}

        with open(f"{args.output_folder}/{new_name}", 'w') as f:
            json.dump(all_data, f, indent=5)









