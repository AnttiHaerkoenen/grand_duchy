import os
import glob


def pdf_to_jpg(directory):
    os.chdir(os.path.expanduser(directory))
    for file in sorted(glob.iglob(f'**/*.pdf', recursive=True)):
        filename = file.split('.')[0]
        os.system(f"pdftoppm {file} {filename} -jpeg")
        print(file)


if __name__ == '__main__':
    pdf_to_jpg('~/sanomalehdet')
