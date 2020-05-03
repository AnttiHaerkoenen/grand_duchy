from pathlib import Path
import json

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL


def populate_database(
        data_dir,
        **database_params
):
    url = URL(**database_params)
    engine = create_engine(url)
    print(engine)


if __name__ == '__main__':
    with open('../../secrets.json') as fopen:
        database_params = json.load(fopen)

    populate_database('foo', **database_params)
