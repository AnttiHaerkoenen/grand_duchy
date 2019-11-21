import os
import subprocess


def remove_whitespaces(directory):
    directory = os.path.expandvars(os.path.expanduser(directory))
    os.chdir(directory)
    for fname in os.listdir(directory):
        if fname.find(" ") >= 0:
            new_fname = fname.replace(" ", "_")
            subprocess.call(['mv', fname, new_fname], shell=False)
        if os.path.isdir(fname):
            os.chdir(fname)
            remove_whitespaces(".")
            os.chdir("..")


if __name__ == '__main__':
    remove_whitespaces('~/sanomalehdet')
