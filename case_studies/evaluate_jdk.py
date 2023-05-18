#!/usr/bin/env python

from sys import path
path.append('../../BabelRTS')
from babelrts import BabelRTS
from babelrts.components.dependency_extractor import LANGUAGE_IMPLEMENTATIONS
from os import walk
from os.path import join, relpath
from time import time
from simpleobject import simpleobject as so
from utils.run_cmd import rc
from utils.openjdk import OpenJDK, get_count, reset_count
from utils.folder_manager import get_repo, dump

JDK_GIT = 'https://github.com/openjdk/jdk.git'

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
    implementations = [implementation for implementation in LANGUAGE_IMPLEMENTATIONS if implementation.get_language() in LANGUAGES]
    implementations.append(OpenJDK)

    jdk = get_repo(JDK_GIT)

    main_source_folder = join(jdk.path, MAIN_SRC_FOLDER)

    java_source_folders = tuple(relpath(source_folder, jdk.path) for source_folder in get_java_source_folders(main_source_folder))
    native_source_folders = tuple(relpath(source_folder, jdk.path) for source_folder in get_native_source_folders(main_source_folder))

    jdk.java_source_folders = len(java_source_folders)
    jdk.native_source_folders = len(native_source_folders)

    babelRTS = BabelRTS(jdk.path, java_source_folders + native_source_folders, TEST_FOLDER, None, LANGUAGES, implementations)

    jdk.commits = []
    for index, sha in enumerate(jdk.shas):
        print(sha)
        rc(f'git checkout {sha}', jdk.path)
        if index:
            commit = so()
            jdk.commits.append(commit)
            reset_count()
            t = time()
            commit.selected_tests = len(babelRTS.rts())
            commit.analysis_time = time() - t
            all_files = babelRTS.get_change_discoverer().get_all_files()
            commit.all_files = len(all_files)
            commit.java_files = sum(1 for file in all_files if file.endswith('.java'))
            commit.native_files = sum(1 for file in all_files if not file.endswith('.java'))
            commit.loc = get_loc(jdk.path, all_files)
            commit.ild = get_count()
            commit.deps = sum(len(v) for v in babelRTS.get_dependency_extractor().get_dependency_graph().values())
            commit.tests = len(babelRTS.get_change_discoverer().get_test_files())
        else:
            babelRTS.rts()

    dump(jdk, 'jdk')

if __name__ == '__main__':
    main()
