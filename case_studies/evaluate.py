#!/usr/bin/env python

from re import compile
from os import walk
from os.path import join, relpath

LOAD_LIBRARY = compile(r'System.loadLibrary\("(.+?)"\)')

JAVA_REPO = 'repos/jdk'
PYTHON_REPO = 'repos/tensorflow'

def get_files(path, extensions):
    for root, dirs, files in walk(path):
        for file in files:
            split = file.rsplit('.', 1)
            if len(split) == 2:
                name, extension = split
                if name and extension and extension in extensions:
                    yield join(root, file)

def get_java_ild():
    for file in get_files(join(JAVA_REPO, 'src'), 'java'):
        rel_path = relpath(file, JAVA_REPO)
        with open(file, 'r') as code:
            for ild in LOAD_LIBRARY.findall(code.read()):
                yield ild, rel_path

def main():
    for ild, file in get_java_ild():
        space = ' ' * (20 - len(ild))
        print(f'{ild}{space}{file}')

if __name__ == '__main__':
    main()
