from pathlib import Path
from typing import Sequence

import pandas as pd
from sqlalchemy import create_engine


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

            df['term'] = [file.stem] * len(df.index)

            if 'type' in df.columns:
                df['lemma'] = df.type.isin(['lemma', 'both'])
                df['regex'] = df.type.isin(['regex', 'both'])
                df.drop(columns='type', inplace=True)

            print(f'Saving {file.stem} to database')

            df.to_sql(
                directory,
                con=engine,
                if_exists='append',
                index=False,
            )

        engine.execute(
            f"CREATE INDEX index ON {directory} (term, year)"
        )


if __name__ == '__main__':
    kwic_dirs = (
        'kwic_sv_riksdag',
        'kwic_fi_newspapers',
    )
    data_dir = Path.home() / '/gd_data/processed'

    with open('../../secrets') as fopen:
        database_url = fopen.read()

    populate_database(
        data_dir=data_dir,
        database_url=database_url,
        kwic_dirs=kwic_dirs,
        size_limit=1_000,
    )

    engine = create_engine(database_url)
    df = pd.read_sql(
        """
        SELECT * 
        FROM keywords
        WHERE regex = true AND term = 'aika'
        """,
        con=engine,
    )

    print(df)
