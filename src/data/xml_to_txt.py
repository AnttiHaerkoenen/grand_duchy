from pathlib import Path
import sys

import xmltodict


def xml_to_txt(input_file, output_file=None):
    if 'xml' not in input_file:
        raise ValueError('File must be in xml format')
    if not output_file:
        output_file = input_file.replace('.xml', '.txt')
    inf = Path(input_file)
    outf = Path(output_file)
    xml = xmltodict.parse(inf.read_text())
    text = xml['pageOCRData']['content']['text']['#text']
    outf.write_text(text)


if __name__ == '__main__':
    files = sys.argv[1:]
    for file in files:
        xml_to_txt(file)
