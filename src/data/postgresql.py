from pathlib import Path
from typing import Sequence
from collections import defaultdict
import time
import logging

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ProgrammingError, OperationalError, NoSuchTableError


class DataBaseError(Exception):
    pass


def retry(retries=10, timeout=5):
    def wraps(f):
        def inner(*args, **kwargs):
            for i in range(retries):
                if i > 0:
                    logging.info(f'Retrying, attempt {i + 1}')
                try:
                    result = f(*args, **kwargs)
                except (ProgrammingError, OperationalError) as e:
                    logging.error(f'Something went wrong: {e}')
                    time.sleep(timeout + i * 10)
                    continue
                except Exception as e:
                    logging.error(f'Unknown error: {e}')
                    continue
                else:
                    return result
            else:
                raise DataBaseError("Database operation failed")
        return inner
    return wraps


@retry(5, 1000)
def populate_database(
        *,
        data_dir: Path,
        kwic_dirs: Sequence,
        database_url: str,
        size_limit: dict,
):
    engine = create_engine(database_url)

    for directory in kwic_dirs:
        path = data_dir / directory
        engine.execute(
            f"DROP TABLE IF EXISTS {directory}"
        )

        for file in sorted(path.iterdir()):
            word_to_sql(engine, directory, file, size_limit)

        create_index(engine, directory)


@retry(10, 10)
def word_to_sql(
        engine: Engine,
        directory: str,
        file: Path,
        size_limit: dict,
):
    logging.debug(f'Reading {file.name}')
    df = pd.read_csv(file)

    if df.empty:
        logging.debug(f'{file.name} is empty, moving on')
        return

    df.sort_values(by='year', inplace=True)
    df = df.head(size_limit[file.stem])
    df.index.rename('index', inplace=False)
    df['term'] = [file.stem] * len(df.index)

    if 'type' in df.columns:
        df['lemma'] = df.type.isin(['lemma', 'both'])
        df['regex'] = df.type.isin(['regex', 'both'])
        df.drop(columns='type', inplace=True)

    logging.info(f'Saving {file.stem} to database')

    df.to_sql(
        directory,
        con=engine,
        if_exists='append',
        index=False,
        chunksize=100,
    )


@retry(20, 10)
def create_index(engine: Engine, directory: str):
    try:
        logging.info("Indexing...")
        engine.execute(
            f"CREATE INDEX {directory}_index ON {directory} (term, year)"
        )
        logging.info(f"Index created for {directory}")
    except NoSuchTableError:
        logging.critical(f"Index creation failed because table '{directory}' does not exist. "
              f"Check if directory '{directory}' is empty.")


def main() -> None:
    logger = logging.getLogger(__name__)
    kwic_dirs = (
        'kwic_sv_riksdag',
        # 'kwic_fi_newspapers',
    )
    data_dir = Path.home() / 'gd_data/processed'

    limit_dict = defaultdict(lambda: 2_000)
    limit_dict['fred'] = 20_000

    with open('secrets') as fopen:
        database_url = fopen.read()

    populate_database(
        data_dir=data_dir,
        database_url=database_url,
        kwic_dirs=kwic_dirs,
        size_limit=limit_dict,
    )

    # engine = create_engine(database_url)
    #
    # df1 = pd.read_sql(
    #     """
    #     SELECT *
    #     FROM kwic_sv_riksdag
    #     WHERE term='parlamentarisk_regering';
    #     """,
    #     con=engine,
    # )
    #
    # df2 = pd.read_sql(
    #     """
    #     SELECT *
    #     FROM kwic_fi_newspapers
    #     WHERE term='suomi';
    #     """,
    #     con=engine,
    # )
    #
    # print(df1)
    # print(df2)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
    