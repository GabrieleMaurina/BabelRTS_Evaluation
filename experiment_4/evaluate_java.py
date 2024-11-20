#!/usr/bin/env python

import glob
import os.path
import pandas
import re
import shutil
import subprocess
import time
import traceback


import babelrts
import utils.args
import utils.folders
import utils.results
import utils.run_rts


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
    if args.sut:
        data = data[data['id'].isin(args.sut)]
    return data


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
    babelrts.BabelRTS(project_folder=TMP_DIR, sources=src,
                      tests=test, languages='java').rts()
    store_cache()
    checkout(id, version, True)
    check_folders(src, test)
    load_cache()
    result = utils.run_rts.run_rts(
        TMP_DIR, src, test, failing_tests, 'java', '.java', id, version, RESULTS_CSV)
    print(result)


def run(args, data, folders):
    print('### Running evaluation ###')
    already_evaluated = set()
    if args.new_faults:
        already_evaluated = utils.results.get_already_evaluated(RESULTS_CSV)

    for project in data.itertuples():
        for version in project.versions:
            if args.new_faults and (project.id, version) in already_evaluated:
                continue
            print(project.id, version)
            src, test = folders.get_folders(project.id, version)
            failing_tests = get_failing_tests(project.id, version, test)
            try:
                run_rts(project.id, version, failing_tests, src, test)
            except Exception:
                print('*** ERROR ***')
                traceback.print_exc()
    # delete_tmp()


def main():
    if not os.path.isdir(RESULTS):
        os.makedirs(RESULTS)
    if not os.path.isdir(REPOS):
        os.makedirs(REPOS)
    args = utils.args.parse_args('Defects4J')
    data = load_data(args)
    folders = utils.folders.Folders(
        SRC_TEST_CSV, SRC_FOLDER, TEST_FOLDER)
    run(args, data, folders)


if __name__ == '__main__':
    main()
