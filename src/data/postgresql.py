from pathlib import Path
from typing import Sequence

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError, OperationalError


def populate_database(
        *,
        data_dir: Path,
        kwic_dirs: Sequence,
        database_url: str,
        size_limit: int,
):
    engine = create_engine(database_url)

    for directory in kwic_dirs:
        path = data_dir / directory

        engine.execute(
            f"DROP TABLE IF EXISTS {directory}"
        )

        for file in sorted(path.iterdir()):
            print(f'Reading {file.name}')

            df = pd.read_csv(file)

            if df.empty:
                print(f'{file.name} is empty, moving on')
                continue

            df.sort_values(by='year', inplace=True)

            df = df.head(size_limit)
            df.index.rename('index', inplace=False)

            df['term'] = [file.stem] * len(df.index)

            if 'type' in df.columns:
                df['lemma'] = df.type.isin(['lemma', 'both'])
                df['regex'] = df.type.isin(['regex', 'both'])
                df.drop(columns='type', inplace=True)

            print(f'Saving {file.stem} to database')

            try:
                df.to_sql(
                    directory,
                    con=engine,
                    if_exists='append',
                    index=False,
                    chunksize=100,
                )
            except OperationalError as e:
                print(f"Database connection shut down: {str(e)}")
                return

        try:
            engine.execute(
                f"CREATE INDEX {directory}_index ON {directory} (term, year)"
            )
            print(f"Index created for {directory}")
        except ProgrammingError:
            print("Index creation failed: Undefined table")


if __name__ == '__main__':
    kwic_dirs = (
        'kwic_sv_riksdag',
        'kwic_fi_newspapers',
    )
    data_dir = Path.home() / 'gd_data/processed'

    with open('../../secrets') as fopen:
        database_url = fopen.read()

    # populate_database(
    #     data_dir=data_dir,
    #     database_url=database_url,
    #     kwic_dirs=kwic_dirs,
    #     size_limit=2000,
    # )

    engine = create_engine(database_url)

    df = pd.read_sql(
        """
        SELECT *
        FROM kwic_sv_riksdag
        WHERE term='ateism';
        """,
        con=engine,
    )

    print(df.columns)
