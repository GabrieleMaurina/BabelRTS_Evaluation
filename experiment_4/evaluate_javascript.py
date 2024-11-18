#!/usr/bin/env python

import os.path
import pandas
import pprint
import subprocess


import babelrts
import utils.args
import utils.folders
import utils.results
import utils.run_rts


DIR = os.path.normpath(os.path.dirname(__file__))
BUGS_JS_DIR = os.path.join(DIR, 'bug-dataset')
BUGS_JS_PROJECTS_CSV = os.path.join(BUGS_JS_DIR, 'Projects.csv')
SRC_TEST_CSV = os.path.join(DIR, 'bugsjs_src_test.csv')
RESULTS = os.path.join(DIR, 'results')
RESULTS_CSV = os.path.join(RESULTS, 'bugsjs_results.csv')
REPOS = os.path.join(DIR, 'repos')

SRC_FOLDER = '.'
TEST_FOLDER = 'test'


def get_faults(args):
    faults = []
    projects = pandas.read_csv(BUGS_JS_PROJECTS_CSV, sep=';')
    for _, project in projects.iterrows():
        if args.sut and project['Name'] not in args.sut:
            continue
        for i in range(1, project['Number of bugs'] + 1):
            fault = {
                'project': project['Name'],
                'github_url': project['Repository url'],
                'bug_id': i,
                'path': os.path.join(REPOS, project['Repository url'].split('/')[-1]),
            }
            faults.append(fault)
    return faults


def get_failing_tests(fault):
    cmd = f'git --no-pager diff --name-only --diff-filter=AM Bug-{fault["bug_id"]} Bug-{fault["bug_id"]}-test'
    files = subprocess.run(
        cmd, shell=True, cwd=fault['path'], check=True, capture_output=True, text=True).stdout
    return set(files.split())


def check_folders(path, src, test):
    if not os.path.isdir(os.path.join(path, src)):
        raise FileNotFoundError(f'{src} not found')
    if not os.path.isdir(os.path.join(path, test)):
        raise FileNotFoundError(f'{test} not found')


def checkout(path, tag):
    cmd = f'git checkout tags/{tag}'
    subprocess.run(cmd, shell=True, cwd=path, check=True, capture_output=True)


def run(args, faults, folders):
    already_evaluated = set()
    if args.new_faults:
        already_evaluated = utils.results.get_already_evaluated(RESULTS_CSV)
    for fault in faults:
        if args.new_faults and (fault['project'], fault['bug_id']) in already_evaluated:
            continue
        if not os.path.isdir(fault['path']):
            subprocess.run(['git', 'clone', fault['github_url'],
                           fault['path']], capture_output=True, check=True)
        fault['failing_tests'] = get_failing_tests(fault)
        checkout(fault['path'], f'Bug-{fault["bug_id"]}-test')
        src, test = folders.get_folders(fault['project'], fault['bug_id'])
        check_folders(fault['path'], src, test)
        babelrts.BabelRTS(fault['path'], src, test,
                          languages='javascript').rts()
        checkout(fault['path'], f'Bug-{fault["bug_id"]}-full')
        check_folders(fault['path'], src, test)
        test_regexp = None
        if fault['project'] == 'Shields':
            test_regexp = r'^.+\.spec\.js$'
        result = utils.run_rts.run_rts(fault['path'], src, test, fault['failing_tests'],
                                       'javascript', '.js', fault['project'], fault['bug_id'], RESULTS_CSV, test_regexp)
        fault['detected'] = result[0]
        fault['time'] = result[1]
        fault['tsr'] = result[2]
        fault['sources'] = result[3]
        fault['tests'] = result[4]
        fault['loc'] = result[5]
        pprint.pprint(fault)


def main():
    if not os.path.isdir(RESULTS):
        os.makedirs(RESULTS)
    if not os.path.isdir(REPOS):
        os.makedirs(REPOS)
    args = utils.args.parse_args('BugsJS')
    faults = get_faults(args)
    folders = utils.folders.Folders(
        SRC_TEST_CSV, SRC_FOLDER, TEST_FOLDER)
    run(args, faults, folders)


if __name__ == '__main__':
    main()
