from pathlib import Path


def text_file_generator(
        data: str,
        rule: str,
):
    fp = Path(data)
    if not fp.exists():
        raise ValueError(f"Specified data path {str(fp)} does not exist")
    for file in fp.rglob(rule):
        text = file.read_text()
        yield str(file), text


if __name__ == '__main__':
    DATA = '../../data/raw'
    texts = sorted(text_file_generator(DATA, 'roa_1809*.txt'))
    print(len(texts))
