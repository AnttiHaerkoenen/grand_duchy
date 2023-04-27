# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from collections import OrderedDict

import click
import xmltodict


def xml_line_generator(xml: OrderedDict):
    if not xml:
        return
    for k, v in xml.items():
        if isinstance(v, list):
            for element in v:
                yield from xml_line_generator(element)
        if isinstance(v, OrderedDict):
            yield from xml_line_generator(v)
        if k == "#text":
            yield v


def xml_converter(input_filepath, output_filepath, logger):
    logger.info(f'Reading {input_filepath}')
    xml = xmltodict.parse(input_filepath.read_text())
    lines = xml_line_generator(xml)
    text = '\n'.join(list(lines))

    logger.info(f'Writing output to {output_filepath}')
    output_filepath.write_text(text)


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """
    Extracts text from a OCRd XML-file
    """
    logger = logging.getLogger(__name__)
    if 'xml' not in input_filepath:
        raise ValueError('File must be in xml format')
    inf = Path(input_filepath)
    outf = Path(output_filepath)
    xml_converter(
        inf,
        outf, 
        logger,
    )


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
