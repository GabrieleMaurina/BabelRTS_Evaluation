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


DIR = os.path.normpath(os.path.dirname(__file__))
DEFECTS4J_CSV = os.path.join(DIR, 'defects4j.csv')
DEFECTS4J_SRC_TEST_CSV = os.path.join(DIR, 'defects4j_src_test.csv')
RESULTS = os.path.join(DIR, 'results')
DEFECTS4J_RESULTS_CSV = os.path.join(RESULTS, 'defects4j_results.csv')
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


def load_folders():
    data = pandas.read_csv(DEFECTS4J_SRC_TEST_CSV, dtype={'version': str})
    data['version'] = data['version'].fillna('')
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


def store_results(id, version, detected, tot_time, test_suite_reduction):
    if os.path.isfile(DEFECTS4J_RESULTS_CSV):
        results = pandas.read_csv(DEFECTS4J_RESULTS_CSV)
        results.loc[-1] = [id, version, detected,
                           tot_time, test_suite_reduction]
        results.drop_duplicates(
            subset=['id', 'version'], keep='last', inplace=True)
        results.sort_values(['id', 'version'], inplace=True, ignore_index=True)
    else:
        results = pandas.DataFrame({'id': [id],
                                    'version': [version],
                                    'detected': [detected],
                                    'selection_time': [tot_time],
                                    'test_suite_reduction': [test_suite_reduction]})
    results.to_csv(DEFECTS4J_RESULTS_CSV, index=False)


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
    test_suite_reduction = 1.0 - \
        len(selected_tests) / len(rts.get_change_discoverer().get_test_files())
    store_results(id, version, detected,
                  tot_time, test_suite_reduction)
    print(f'\t\t{detected}, {tot_time}, {test_suite_reduction}')


def get_folders(folders, project, version):
    rows = folders[folders['identifier'] == project]
    for row in rows.itertuples():
        if not row.version:
            return row.src, row.test
        try:
            if row.version.startswith('-'):
                raise ValueError
            value = int(row.version)
        except ValueError:
            values = row.version.split('-')
            start = int(values[0]) if values[0] else None
            end = int(values[1]) if values[1] else None
            if start is None and end is None:
                return row.src, row.test
            elif start is None:
                if version <= end:
                    return row.src, row.test
            elif end is None:
                if version >= start:
                    return row.src, row.test
            else:
                if start <= version <= end:
                    return row.src, row.test
        else:
            if value == version:
                return row.src, row.test

    return SRC_FOLDER, TEST_FOLDER


def run(args, data, folders):
    print('### Running evaluation ###')
    already_evaluated = set()
    if args.new_faults and os.path.isfile(DEFECTS4J_RESULTS_CSV):
        results = pandas.read_csv(DEFECTS4J_RESULTS_CSV)
        for row in results.itertuples():
            already_evaluated.add((row.id, row.version))
    for project in data.itertuples():
        print('Id:', project.id)
        for version in project.versions:
            print('\tFault:', version)
            if args.new_faults and (project.id, version) in already_evaluated:
                print('\t\tSkipping')
                continue
            src, test = get_folders(folders, project.id, version)
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
    folders = load_folders()
    run(args, data, folders)


if __name__ == '__main__':
    main()
