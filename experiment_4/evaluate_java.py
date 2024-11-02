#!/usr/bin/env python

import argparse
import glob
import os.path
import pandas
import re
import shutil
import subprocess
import time
import traceback


import babelrts
import utils.folders
import utils.results


DIR = os.path.normpath(os.path.dirname(__file__))
DEFECTS4J_CSV = os.path.join(DIR, 'defects4j.csv')
SRC_TEST_CSV = os.path.join(DIR, 'defects4j_src_test.csv')
RESULTS = os.path.join(DIR, 'results')
RESULTS_CSV = os.path.join(RESULTS, 'defects4j_results.csv')
REPOS = os.path.join(DIR, 'repos')
TMP_DIR = os.path.join(REPOS, 'tmp')
CACHE_DIR = os.path.join(REPOS, 'cache')
CACHE = '.babelrts'

TESTS_SECTION_RE = re.compile(
    r'Root cause in triggering tests:\n([\s\S]+?)\n-------------------')
TESTS_RE = re.compile(r' - ([\w.]+)::.+\n')

SRC_FOLDER = 'src/main/java'
TEST_FOLDER = 'src/test/java'


def get_failing_tests(id, version, test_folder):
    cmd = f'defects4j info -p {id} -b {version}'
    info = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, check=True).stdout
    tests_section = TESTS_SECTION_RE.search(info).group(1)
    tests = TESTS_RE.findall(tests_section)
    return {os.path.join(test_folder, test.replace('.', '/')) + '.java' for test in tests}


def expand_versions(versions):
    expanded = set()
    versions = versions.split('|')
    for value in versions:
        if '-' in value:
            start, end = value.split('-')
            start = int(start)
            end = int(end)
            expanded.update(range(start, end + 1))
        else:
            expanded.add(int(value))
    return tuple(expanded)


def load_data(args):
    data = pandas.read_csv(DEFECTS4J_CSV)
    data['versions'] = data['versions'].apply(expand_versions)
    if args.identifier:
        data = data[data['id'].isin(args.identifier)]
    return data


def parse_args():
    parser = argparse.ArgumentParser(
        description='Evaluate babelrts on defects4j')
    parser.add_argument('-i', '--identifier', nargs='+',
                        default=(), help='Project identifier')
    parser.add_argument('-n', '--new-faults', action='store_true', default=False,
                        help='Only evaluate new faults')
    args = parser.parse_args()
    return args


def delete_dir(dir):
    if os.path.isdir(dir):
        for _ in range(3):
            try:
                shutil.rmtree(dir)
                break
            except Exception:
                time.sleep(1)


def delete_tmp():
    delete_dir(TMP_DIR)


def delete_cache():
    delete_dir(CACHE_DIR)


def checkout(id, version, fixed=False):
    delete_tmp()
    v = 'f' if fixed else 'b'
    cmd = f'defects4j checkout -p {id} -v {version}{v} -w {TMP_DIR}'
    subprocess.run(cmd, shell=True, check=True, capture_output=True)


def store_cache():
    delete_cache()
    os.makedirs(CACHE_DIR)
    for path in glob.glob(os.path.join(TMP_DIR, CACHE)):
        shutil.move(path, CACHE_DIR)


def load_cache():
    for path in glob.glob(os.path.join(CACHE_DIR, CACHE)):
        shutil.move(path, TMP_DIR)
    delete_cache()


def check_folders(src, test):
    if not os.path.isdir(os.path.join(TMP_DIR, src)):
        raise FileNotFoundError(f'{src} not found')
    if not os.path.isdir(os.path.join(TMP_DIR, test)):
        raise FileNotFoundError(f'{test} not found')


def run_rts(id, version, failing_tests, src, test):
    checkout(id, version)
    check_folders(src, test)
    rts = babelrts.BabelRTS(project_folder=TMP_DIR,
                            sources=src, tests=test, languages='java')
    rts.rts()
    store_cache()
    checkout(id, version, True)
    check_folders(src, test)
    load_cache()
    rts = babelrts.BabelRTS(project_folder=TMP_DIR,
                            sources=src, tests=test, languages='java')
    tot_time = time.time()
    selected_tests = rts.rts()
    tot_time = time.time() - tot_time
    selected_tests = set(selected_tests)
    detected = failing_tests.issubset(selected_tests)
    tests = rts.get_change_discoverer().get_test_files()
    sources = rts.get_change_discoverer().get_source_files()
    test_suite_reduction = 1.0 - len(selected_tests) / len(tests)
    loc = utils.results.get_loc(TMP_DIR, '.java')
    utils.results.store_results(RESULTS_CSV, id, version, detected,
                                tot_time, test_suite_reduction, len(sources), len(tests), loc)
    print(f'\t\t{detected}, {tot_time}, {test_suite_reduction}')


def run(args, data, folders):
    print('### Running evaluation ###')
    already_evaluated = set()
    if args.new_faults:
        already_evaluated = utils.results.get_already_evaluated(RESULTS_CSV)

    for project in data.itertuples():
        print('Id:', project.id)
        for version in project.versions:
            print('\tFault:', version)
            if args.new_faults and (project.id, version) in already_evaluated:
                print('\t\tSkipping')
                continue
            src, test = folders.get_folders(project.id, version)
            failing_tests = get_failing_tests(project.id, version, test)
            try:
                run_rts(project.id, version, failing_tests, src, test)
            except Exception as e:
                print('\t\t*** ERROR ***')
                traceback.print_exc()
    delete_tmp()


def main():
    if not os.path.isdir(RESULTS):
        os.makedirs(RESULTS)
    if not os.path.isdir(REPOS):
        os.makedirs(REPOS)
    args = parse_args()
    data = load_data(args)
    folders = utils.folders.Folders(
        SRC_TEST_CSV, SRC_FOLDER, TEST_FOLDER)
    run(args, data, folders)


if __name__ == '__main__':
    main()
