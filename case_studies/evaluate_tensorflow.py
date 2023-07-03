#!/usr/bin/env python


from sys import path
path.append('../../BabelRTS')
from babelrts import BabelRTS
from babelrts.components.dependency_extractor import LANGUAGE_IMPLEMENTATIONS

from utils.ilts import count_ilts
from utils.loc import get_loc
from utils.revisions import add_shas
from utils.folder_manager import get_repo, dump
from utils.tensorflow import Tensorflow, get_count, reset_count
from utils.run_cmd import rc
from simpleobject import simpleobject as so
from time import time

TENSORFLOW_GIT = 'https://github.com/tensorflow/tensorflow.git'

SRC_FOLDERS = ['tensorflow/core', 'tensorflow/python']
TEST_FOLDERS = ['tensorflow/python/kernel_tests']

LANGUAGES = ('python', 'c++', 'tensorflow')


def main():
    implementations = [
        implementation for implementation in LANGUAGE_IMPLEMENTATIONS if implementation.get_language() in LANGUAGES]
    implementations.append(Tensorflow)

    print('Cloning')
    tensorflow = get_repo(TENSORFLOW_GIT)
    add_shas(tensorflow, ('java'))

    print(tensorflow.shas)
    return

    print('RTS')
    babelRTS = BabelRTS(tensorflow.path, SRC_FOLDERS,
                        TEST_FOLDERS, None, LANGUAGES, implementations)

    tensorflow.commits = []
    for index, sha in enumerate(tensorflow.shas):
        print(sha)
        rc(f'git checkout {sha}', tensorflow.path)
        if index:
            commit = so()
            tensorflow.commits.append(commit)
            reset_count()
            t = time()
            commit.selected_tests = len(babelRTS.rts())
            commit.analysis_time = time() - t
            all_files = babelRTS.get_change_discoverer().get_all_files()
            commit.all_files = len(all_files)
            commit.python_files = sum(
                1 for file in all_files if file.endswith('.py'))
            commit.native_files = sum(
                1 for file in all_files if not file.endswith('.py'))
            commit.loc = get_loc(tensorflow.path, all_files)
            commit.ild = get_count()
            commit.ilt = count_ilts(babelRTS)
            commit.deps = sum(len(v) for v in babelRTS.get_dependency_extractor(
            ).get_dependency_graph().values())
            commit.tests = len(
                babelRTS.get_change_discoverer().get_test_files())
            commit.changed = len(
                babelRTS.get_change_discoverer().get_changed_files())
            print(commit)
        else:
            babelRTS.rts()

    dump(tensorflow, 'tensorflow')


if __name__ == '__main__':
    main()
