# -*- coding: utf-8 -*-
import logging
import os
from pathlib import Path
import re
import shutil

import click
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup

from xml_to_txt import xml_converter


@click.command()
@click.argument('url', type=click.STRING)
@click.argument('pdf_filepath', type=click.Path())
@click.argument('output_filepath', type=click.Path())
def main(url, pdf_filepath, output_filepath):
    """
    Download pdfs from riksdagstryck site
    """
    logger = logging.getLogger(__name__)
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    url = url.rstrip('/')
    logger.info(f"Downloading a list of directories from {url}")
    try:
        r = requests.get(url=url, headers=headers)
    except ConnectionError as e:
        logger.error(f'Connection failed: {e}')
        return
    soup = BeautifulSoup(r.content, features='html.parser')
    dirs = [link.get('href') for link in soup.find_all('a') if re.search('\d{4}', link.string)]

    os.chdir(pdf_filepath)
    for dir_ in dirs:
        dir_url = f'{url}/{dir_}'
        logger.info(f'Downloading pdfs from {dir_}')
        os.system(f'wget -r -np -l 1 ~/gd_data/raw/ -e robots=off {dir_url}')
        logger.info(f'Converting pdfs from {dir_url} to xml in {output_filepath}')
        for pdf_fp in Path(dir_url).glob(f'*.pdf'):
            xml_fp = output_filepath / f'{pdf_fp.stem}.txt'
            xml_converter(pdf_fp, xml_fp)
        logger.info(f'Removing dir {dir_url}')
        shutil.rmtree(Path('weburn.kb.se/riks/ståndsriksdagen/pdf') / dir_)
    logger.info('Download and transform complete')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_file = Path('./logs') / Path(__file__).stem
    logging.basicConfig(filename=log_file, level=logging.INFO, format=log_fmt)

    main()
