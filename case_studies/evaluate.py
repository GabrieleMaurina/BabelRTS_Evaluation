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
import utils.subjects as subjects
from simpleobject import simpleobject as so
from time import time
from os.path import splitext, basename
import utils.tensorflow as tf
import utils.openjdk as openjdk
from process_changes import load_changes_csv
from progressbar import progressbar

LANGUAGE_IMPLEMENTATIONS += (tf.Tensorflow, openjdk.OpenJDK)

def is_test(path):
    name, _ = splitext(basename(path))
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


def main(subject, run, history):
    data = so(load(subjects.META[subject]))
    if history:
        shas = tuple(load_changes_csv(subject).hashcode.iloc[-history-1:])
        data.shas = shas

    languages = subjects.RUNS[subject][run]
    implementations = []
    for implementation in LANGUAGE_IMPLEMENTATIONS:
        if implementation.get_language() in languages:
            implementations.append(implementation)
        
    src_folders = subjects.SRC_FOLDERS[subject]()
    test_folders = subjects.TEST_FOLDERS[subject]()

    babelRTS = BabelRTS(data['path'], src_folders, test_folders, None, languages, implementations)

    data.commits = []
    print('starting loop')
    for index, sha in progressbar(enumerate(data.shas), max_value=len(data.shas)):
        print('\nchecking out', sha)
        rc(f'git checkout {sha}', data.path)
        if index:
            commit = so()
            commit.sha = sha
            data.commits.append(commit)
            tf.reset_count()
            t = time()
            print('exploring codebase')
            babelRTS.get_change_discoverer().explore_codebase()
            print('checking additional tests')
            check_additional_tests(babelRTS.get_change_discoverer())
            print('generating dependency graph')
            babelRTS.get_dependency_extractor().generate_dependency_graph()
            print('selecting tests')
            babelRTS.get_test_selector().select_tests()
            commit.analysis_time = time() - t
            print('computing stats')
            commit.files = count_files(babelRTS)
            commit.loc = get_loc(
                data.path, babelRTS.get_change_discoverer().get_all_files())
            commit.ild = tf.get_count()
            commit.tests = count_tests(babelRTS)
            commit.deps = sum(len(v) for v in babelRTS.get_dependency_extractor(
            ).get_dependency_graph().values())
            commit.selected_tests = tuple(
                babelRTS.get_test_selector().get_selected_tests())
            print('completed')
        else:
            print('initializing babelrts')
            babelRTS.rts(True)

    dump(data, f'{subject}_{"history_" if history else ""}' + run)


if __name__ == '__main__':
    subject, run  = argv[1:3]
    history = int(argv[3]) if len(argv) > 3 else None
    main(subject, run, history)
