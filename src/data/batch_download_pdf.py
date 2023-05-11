# -*- coding: utf-8 -*-
import logging
import os
import subprocess
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
@click.option('--filter', 'filter_rule', type=click.STRING, default='.', help='regular expression for selecting downloaded directories')
def main(url, pdf_filepath, output_filepath, filter_rule):
    """
    Download pdfs from riksdagstryck site
    """
    logger = logging.getLogger(__name__)
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    url = url.rstrip('/')
    output_fp = Path(output_filepath)
    if not output_fp.is_dir():
        output_fp.mkdir()

    try:
        re.compile(filter_rule)
    except re.error as e:
        logger.error(f'{filter_rule} is not valid regex, using default (all) - {e}')
        filter_rule = '.'

    logger.info(f"Downloading a list of directories from {url}")
    try:
        r = requests.get(url=url, headers=headers)
    except ConnectionError as e:
        logger.error(f'Connection failed, exiting - {e}')
        return

    soup = BeautifulSoup(r.content, features='html.parser')
    dirs = [link.get('href').rstrip('/') for link in soup.find_all('a') if re.search('\d{4}', link.string)]
    dir_filter = lambda x: re.search(filter_rule, x)

    os.chdir(pdf_filepath)
    for dir_ in filter(dir_filter, dirs):
        dir_url = f'{url}/{dir_}'
        logger.info(f'Downloading pdfs from {dir_}')
        try:
            sub_wget = subprocess.run(['wget', '-r', '-np', '-l 1', '-e robots=off', dir_url], capture_output=True)
            logger.info(f'wget finished with exit code {sub_wget.returncode}')
            sub_wget.check_returncode()
        except subprocess.CalledProcessError as e:
            logger.error(f'wget failed when downloading {dir_}, exiting - {e}')
            return
        
        dir_fp = Path.cwd() / 'weburn.kb.se/riks/ståndsriksdagen/pdf' / dir_
        logger.info(f'Converting pdfs from {dir_fp} to txt in {output_filepath}')
        pdf_list = list(dir_fp.glob('**/*.pdf'))
        for pdf_fp in pdf_list:
            try:
                txt_fp = output_fp / f'{pdf_fp.stem}.txt'
                sub_pdftotext = subprocess.run(['pdftotext', '-enc', 'UTF-8', pdf_fp, txt_fp], capture_output=True)
                logger.info(f'pdftotext finished with exit code {sub_pdftotext.returncode}')
                sub_pdftotext.check_returncode()
                logger.info(f'{pdf_fp} converted and saved to {txt_fp}')
            except subprocess.CalledProcessError as e:
                logger.error(f'pdftotext failed, exiting - {e}')
                return
        logger.info(f'Removing dir {dir_fp}')
        shutil.rmtree(dir_fp)
    logger.info('Download and transformation complete')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_file = Path('./logs') / Path(__file__).stem
    logging.basicConfig(filename=log_file, level=logging.INFO, format=log_fmt)

    main()
