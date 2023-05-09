# -*- coding: utf-8 -*-
import logging
import os
from pathlib import Path

import click


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """
    Extracts text from OCR'd PDF-files
    """
    logger = logging.getLogger(__name__)
    logger.info(f'Reading files from {input_filepath}')
    input_fp = Path(input_filepath)
    output_fp = Path(output_filepath)
    if not output_fp.is_dir():
        output_fp.mkdir()
    pdf_list = list(input_fp.glob('**/*.pdf'))
    for fp in pdf_list:
        outf = output_fp / f'{fp.stem}.txt'
        logger.info(f'Reading pdf from {fp}')
        os.system(f'pdftotext {fp} {outf} -enc UTF-8')
        logger.info(f'Saved to {outf}')
    logger.info(f'Finished writing results to {output_filepath}')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_file = Path('./logs') / Path(__file__).stem
    logging.basicConfig(filename=log_file, level=logging.INFO, format=log_fmt)

    main()
