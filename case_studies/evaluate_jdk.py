#!/usr/bin/env python

from sys import path, argv
path.append('../../BabelRTS')
from babelrts import BabelRTS
from os import walk
from os.path import join, relpath

#LOAD_LIBRARY = compile(r'System.loadLibrary\("(.+?)"\)')

JDK = 'repos/jdk'

MAIN_SRC_FOLDER = 'src'
TEST_FOLDER = 'test'

def get_java_source_folders(path):
    for root, dirs, files in walk(path):
        if 'classes' in dirs:
            yield join(root, 'classes')

def get_native_source_folders(path):
    for root, dirs, files in walk(path):
        if 'native' in dirs:
            yield join(root, 'native')

def main():
    main_source_folder = join(JDK, MAIN_SRC_FOLDER)

    java_source_folders = tuple(relpath(source_folder, JDK) for source_folder in get_java_source_folders(main_source_folder))
    native_source_folders = tuple(relpath(source_folder, JDK) for source_folder in get_native_source_folders(main_source_folder))

    print(java_source_folders)
    print(native_source_folders)

    babelRTS = BabelRTS(JDK, java_source_folders + native_source_folders, TEST_FOLDER, None, ('java', 'c++'))

if __name__ == '__main__':
    main()
