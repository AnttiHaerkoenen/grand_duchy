# -*- coding: utf-8 -*-
import logging
from pathlib import Path

import click

from xml_to_txt import xml_converter


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ 
    Extracts text from OCRd XML-files
    """
    logger = logging.getLogger(__name__)
    logger.info(f'Reading files from {input_filepath}')
    input_fp = Path(input_filepath)
    output_fp = Path(output_filepath)
    output_fp.mkdir(exist_ok=True)
    xml_list = list(input_fp.glob('**/*.xml'))
    for fp in xml_list:
        outf = output_fp / f'{fp.stem}.txt'
        xml_converter(fp, outf, logger)
    logger.info(f'Finished writing results to {output_filepath}')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()