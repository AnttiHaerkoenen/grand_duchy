from pathlib import Path


def text_file_generator(
        data: str,
        file_extension: str = 'txt',
):
    fp = Path(data)
    if not fp.exists():
        raise ValueError(f"Specified data path {str(fp)} does not exist")
    for file in fp.rglob(f'*.{file_extension}'):
        text = file.read_text()
        yield text


if __name__ == '__main__':
    DATA = '../../data/raw'
    texts = sorted(text_file_generator(DATA))
    print(len(texts))
