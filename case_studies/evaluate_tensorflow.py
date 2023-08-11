#!/usr/bin/env python


from sys import path
path.append('../../BabelRTS')
from babelrts import BabelRTS
from babelrts.components.dependency_extractor import LANGUAGE_IMPLEMENTATIONS

from sys import argv
from utils.ilt import count_tests
from utils.loc import get_loc
from utils.folder_manager import dump, load
from utils.run_cmd import rc
from download_repos import TENSORFLOW_META
from simpleobject import simpleobject as so
from time import time
from os.path import splitext, basename
import utils.tensorflow as tf
import utils.openjdk as ojdk

SRC_FOLDERS = ['tensorflow/core', 'tensorflow/python',
               'tensorflow/java/src/main/java', 'tensorflow/java/src/main/native']
TEST_FOLDERS = ['tensorflow/python/kernel_tests',
                'tensorflow/java/src/test/java']

PYTHON = 'python'
CPP = 'c++'
JAVA = 'java'
TENSORFLOW = 'tensorflow'
OPENJDK = 'openjdk'
LANGUAGE_IMPLEMENTATIONS += (tf.Tensorflow, ojdk.OpenJDK)

RUNS = {
    PYTHON: (PYTHON,),
    CPP: (CPP,),
    JAVA: (JAVA,),
    'all': (PYTHON, CPP, JAVA, TENSORFLOW, OPENJDK)
}


def is_test(path):
    name, extension = splitext(basename(path))
    return name.lower().endswith('test')


def check_additional_tests(change_discoverer):
    source_files = change_discoverer.get_source_files()
    test_files = change_discoverer.get_test_files()
    for source_file in tuple(source_files):
        if is_test(source_file):
            test_files.add(source_file)
            source_files.remove(source_file)


def count_file_type(files):
    data = so(cpp=0, java=0, python=0)
    for file in files:
        if file.endswith('.java'):
            data.java += 1
        elif file.endswith('.py'):
            data.python += 1
        else:
            data.cpp += 1
    return data


def count_files(babelRTS):
    data = so()

    change_discoverer = babelRTS.get_change_discoverer()
    data.source_files = count_file_type(
        change_discoverer.get_source_files())
    data.test_files = count_file_type(change_discoverer.get_test_files())
    data.changed = count_file_type(change_discoverer.get_changed_files())

    test_selector = babelRTS.get_test_selector()
    data.selected_tests = count_file_type(test_selector.get_selected_tests())

    return data


def main():
    run = argv[1]

    tensorflow = so(load(TENSORFLOW_META))

    languages = RUNS[run]
    implementations = []
    for implementation in LANGUAGE_IMPLEMENTATIONS:
        if implementation.get_language() in RUNS[run]:
            implementations.append(implementation)

    babelRTS = BabelRTS(tensorflow['path'], SRC_FOLDERS,
                        TEST_FOLDERS, None, languages, implementations)

    tensorflow.commits = []
    for index, sha in enumerate(tensorflow.shas):
        print(sha)
        rc(f'git checkout {sha}', tensorflow.path)
        if index:
            commit = so()
            commit.sha = sha
            tensorflow.commits.append(commit)
            tf.reset_count()
            ojdk.reset_count()
            t = time()
            babelRTS.get_change_discoverer().explore_codebase()
            check_additional_tests(babelRTS.get_change_discoverer())
            babelRTS.get_dependency_extractor().generate_dependency_graph()
            babelRTS.get_test_selector().select_tests()
            commit.analysis_time = time() - t

            commit.files = count_files(babelRTS)

            commit.loc = get_loc(
                tensorflow.path, babelRTS.get_change_discoverer().get_all_files())
            commit.p2c = tf.get_count()
            commit.j2c = ojdk.get_count()
            commit.ild = commit.p2c + commit.j2c
            commit.tests = count_tests(babelRTS)
            commit.deps = sum(len(v) for v in babelRTS.get_dependency_extractor(
            ).get_dependency_graph().values())
            commit.selected_tests = tuple(
                babelRTS.get_test_selector().get_selected_tests())
        else:
            babelRTS.rts()

    dump(tensorflow, 'tensorflow_' + run)


if __name__ == '__main__':
    main()
