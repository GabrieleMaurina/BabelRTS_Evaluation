#!/usr/bin/env python

import configparser
import os.path
import pprint
import subprocess

import babelrts
import utils.args
import utils.run_rts
import utils.folders
import utils.results


DIR = os.path.abspath(os.path.dirname(__file__))
BUGS_IN_PY_DIR = os.path.join(DIR, 'BugsInPy', 'projects')
BUGS_IN_PY_SRC_TEST_CSV = os.path.join(DIR, 'bugsinpy_src_test.csv')
REPOS = os.path.join(DIR, 'repos')
RESULTS = os.path.join(DIR, 'results')
RESULTS_CSV = os.path.join(RESULTS, 'bugsinpy_results.csv')
BABELRTS_CACHE = '.babelrts'


SRC_FOLDER = 'src'
TEST_FOLDER = 'tests'


def read_config(path):
    parser = configparser.ConfigParser()
    with open(path, 'r') as f:
        data = f.read()
    parser.read_string(f'[DEFAULT]\n{data}')
    return dict(parser.items('DEFAULT'))


def get_faults(args):
    faults = []
    for root, projects, _ in os.walk(BUGS_IN_PY_DIR):
        for project in projects:
            project_dir = os.path.join(root, project)
            bugs_dir = os.path.join(project_dir, 'bugs')
            project_info = os.path.join(project_dir, 'project.info')
            info = read_config(project_info)
            github_url = info['github_url'].strip('"')
            for bugs_root, bugs, _ in os.walk(bugs_dir):
                for bug in bugs:
                    bug_dir = os.path.join(bugs_root, bug)
                    bug_info = os.path.join(bug_dir, 'bug.info')
                    info = read_config(bug_info)
                    fault = {
                        'project': project,
                        'path': os.path.join(REPOS, project),
                        'github_url': github_url,
                        'bug_id': int(bug),
                        'buggy_commit': info['buggy_commit_id'].strip('"'),
                        'fixed_commit': info['fixed_commit_id'].strip('"'),
                        'failing_tests': info['test_file'].strip('"').split(';'),
                    }
                    faults.append(fault)
                break
        break
    if args.sut:
        faults = [fault for fault in faults if fault['project'] in args.sut]
    if args.new_faults:
        already_evaluated = utils.results.get_already_evaluated(RESULTS_CSV)
        faults = [fault for fault in faults if (
            fault['project'], fault['bug_id']) not in already_evaluated]
    faults.sort(key=lambda x: (x['project'], x['bug_id']))
    return faults


def check_folders(path, src, test):
    if not os.path.isdir(os.path.join(path, src)):
        raise FileNotFoundError(f'{src} not found')
    if not os.path.isdir(os.path.join(path, test)):
        raise FileNotFoundError(f'{test} not found')


def evaluate_fault(fault, folders):
    if not os.path.isdir(fault['path']):
        subprocess.run(['git', 'clone', fault['github_url'],
                       fault['path']], capture_output=True, check=True)
    subprocess.run(['git', 'checkout', fault['buggy_commit']],
                   cwd=fault['path'], capture_output=True, check=True)
    src, test = folders.get_folders(fault['project'], fault['bug_id'])
    check_folders(fault['path'], src, test)
    babelrts.BabelRTS(fault['path'], src, test, languages='python').rts()
    subprocess.run(['git', 'checkout', fault['fixed_commit']],
                   cwd=fault['path'], capture_output=True, check=True)
    check_folders(fault['path'], src, test)
    failing_tests = set(fault['failing_tests'])
    result = utils.run_rts.run_rts(fault['path'], src, test, failing_tests,
                                   'python', '.py', fault['project'], fault['bug_id'], RESULTS_CSV)
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
    args = utils.args.parse_args('BugsInPy')
    folders = utils.folders.Folders(
        BUGS_IN_PY_SRC_TEST_CSV, SRC_FOLDER, TEST_FOLDER)
    faults = get_faults(args)
    for fault in faults:
        evaluate_fault(fault, folders)


if __name__ == '__main__':
    main()
