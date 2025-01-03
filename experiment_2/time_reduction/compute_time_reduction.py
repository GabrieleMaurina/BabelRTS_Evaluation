#!/usr/bin/env python

import json
import babelrts
import googletest
import mochiweb
import graphql
import faker
import os.path
import pandas
import subprocess
import time


N_REV = 30
TOT_REV = N_REV + 1


DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(DIR, os.pardir))
SUBJECTS_DIR = os.path.join(ROOT_DIR, 'subjects')
RESULTS_DIR = os.path.join(ROOT_DIR, 'results')
RESULTS_FILE = os.path.join(RESULTS_DIR, 'time_reduction.csv')


BABELRTS_CACHE = '.babelrts'


SUTS = [mochiweb.Mochiweb(), graphql.Graphql(), faker.Faker(), googletest.GoogleTest()]
SUTS = [googletest.GoogleTest()]


def get_first_commit(sut):
    if isinstance(sut.language, str):
        name = f'{sut.language}_results.csv'
    else:
        name = '_'.join(sut.language) + '_results.csv'
    path = os.path.join(RESULTS_DIR, name)
    with open(path, 'r') as f:
        for line in f:
            if line.startswith(sut.name):
                return line.split(',')[1]


def get_src_test(sut):
    if isinstance(sut.language, str):
        name = f'{sut.language}_subjects.csv'
    else:
        name = '_'.join(sut.language) + '_subjects.csv'
    path = os.path.join(SUBJECTS_DIR, name)
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if sut.name in line:
                return line.split(',')[2:0:-1]


def get_all_commits(sut):
    result = subprocess.run(['git', '--no-pager', 'log', '--first-parent', '--pretty=tformat:%H',
                             f'--max-count={TOT_REV}'], cwd=sut.path, check=True, capture_output=True, text=True)
    return tuple(reversed(result.stdout.splitlines()))


def checkout_commit(commit, sut):
    subprocess.run(['git', 'clean', '-fd'], cwd=sut.path,
                   check=True, capture_output=True)
    subprocess.run(['git', 'reset', '--hard'], cwd=sut.path,
                   check=True, capture_output=True)
    subprocess.run(['git', 'checkout', '-f', commit], cwd=sut.path,
                   check=True, capture_output=True)


def save_results(sut, avg_time_retest_all, avg_time_rts, avg_time_reduction):
    if os.path.isfile(RESULTS_FILE):
        results = pandas.read_csv(RESULTS_FILE)
        results.loc[-1] = [sut.name, avg_time_retest_all,
                           avg_time_rts, avg_time_reduction]
        results.drop_duplicates('sut', keep='last', inplace=True)
        results.sort_values(['sut'], inplace=True, ignore_index=True)
    else:
        results = pandas.DataFrame({'sut': [sut.name],
                                    'avg_time_retest_all': [avg_time_retest_all],
                                    'avg_time_rts': [avg_time_rts],
                                    'avg_time_reduction': [avg_time_reduction],
                                    })
    results.to_csv(RESULTS_FILE, index=False)


def read_babelrts_cache(sut):
    with open(os.path.join(sut.path, BABELRTS_CACHE), 'r') as f:
        return json.load(f)
    

def write_babelrts_cache(sut, cache):
    with open(os.path.join(sut.path, BABELRTS_CACHE), 'w') as f:
        json.dump(cache, f, indent=4)


def process_sut(sut):
    first_commit = get_first_commit(sut)
    src, test = get_src_test(sut)
    checkout_commit(first_commit, sut)
    commits = get_all_commits(sut)
    results = {'time_retest_all': [], 'time_rts': [], 'time_reduction': []}
    cache = {}
    for index, commit in enumerate(commits):
        checkout_commit(commit, sut)
        sut.build()
        if index == 0:
            babelrts.BabelRTS(sut.path, src, test, languages=sut.language).rts()
            cache = read_babelrts_cache(sut)
            continue
        time_run_all = sut.run_all_tests()
        babelRTS = babelrts.BabelRTS(
            sut.path, src, test, languages=sut.language)
        write_babelrts_cache(sut, cache)
        start = time.time()
        selected_tests = babelRTS.rts()
        end = time.time()
        cache = read_babelrts_cache(sut)
        time_rts = end - start + sut.run_tests(selected_tests)
        time_reduction = (time_run_all - time_rts) / time_run_all
        results['time_retest_all'].append(time_run_all)
        results['time_rts'].append(time_rts)
        results['time_reduction'].append(time_reduction)
        print(sut.name, index, commit, time_run_all, time_rts, time_reduction)
    avg_time_retest_all = sum(results['time_retest_all']) / N_REV
    avg_time_rts = sum(results['time_rts']) / N_REV
    avg_time_reduction = sum(results['time_reduction']) / N_REV
    save_results(sut, avg_time_retest_all, avg_time_rts, avg_time_reduction)


def main():
    for sut in SUTS:
        process_sut(sut)


if __name__ == '__main__':
    main()
