#!/usr/bin/env python

from sys import path, argv
path.append('../../BabelRTS')
from babelrts import BabelRTS
from babelrts.components.dependency_extractor import LANGUAGE_IMPLEMENTATIONS
from os import walk
from os.path import join, relpath
from time import time
from simpleobject import simpleobject as so
from utils.run_cmd import rc
from utils.openjdk import OpenJDK, get_count, reset_count

JDK_PATH = 'repos/jdk'

MAIN_SRC_FOLDER = 'src'
TEST_FOLDER = 'test'

LANGUAGES = ('java', 'c++', 'openjdk')

def get_java_source_folders(path):
    for root, dirs, files in walk(path):
        if 'classes' in dirs:
            yield join(root, 'classes')

def get_native_source_folders(path):
    for root, dirs, files in walk(path):
        if 'native' in dirs:
            yield join(root, 'native')

def get_loc(root, files):
    if files:
        K = 100
        files = tuple(files)
        partition = (files[i:i+K] for i in range(0, len(files), K))
        def loc(paths):
            return int(rc(f'wc -l ' + ' '.join(paths), root).stdout.split('\n')[-2].rsplit(' ', 1)[0])
        return sum(loc(paths) for paths in partition)
    else:
        return 0

def main():
    jdk = so()

    main_source_folder = join(JDK_PATH, MAIN_SRC_FOLDER)

    java_source_folders = tuple(relpath(source_folder, JDK_PATH) for source_folder in get_java_source_folders(main_source_folder))
    native_source_folders = tuple(relpath(source_folder, JDK_PATH) for source_folder in get_native_source_folders(main_source_folder))

    jdk.java_source_folders = len(java_source_folders)
    jdk.native_source_folders = len(native_source_folders)

    implementations = [implementation for implementation in LANGUAGE_IMPLEMENTATIONS if implementation.get_language() in LANGUAGES]
    implementations.append(OpenJDK)

    reset_count()

    t = time()
    babelRTS = BabelRTS(JDK_PATH, java_source_folders + native_source_folders, TEST_FOLDER, None, LANGUAGES, implementations)
    babelRTS.get_change_discoverer().explore_codebase()
    #babelRTS.get_dependency_extractor().generate_dependency_graph()
    #babelRTS.test_selector().select_tests()
    t = time() - t
    jdk.analysis_time = t

    all_files = babelRTS.get_change_discoverer().get_all_files()
    jdk.all_files = len(all_files)
    jdk.java_files = sum(1 for file in all_files if file.endswith('.java'))
    jdk.native_files = sum(1 for file in all_files if not file.endswith('.java'))
    jdk.loc = get_loc(JDK_PATH, all_files)

    jdk.ild = get_count()

    print(jdk)

if __name__ == '__main__':
    main()
