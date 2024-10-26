#!/usr/bin/env python

import babelrts
import configparser
import os.path
import subprocess


DIR = os.path.abspath(os.path.dirname(__file__))
BUGS_IN_PY_DIR = os.path.join(DIR, 'BugsInPy', 'projects')
REPOS = os.path.join(DIR, 'repos')
BABELRTS_CACHE = '.babelrts'


def read_config(path):
    parser = configparser.ConfigParser()
    with open(path, 'r') as f:
        data = f.read()
    parser.read_string(f'[DEFAULT]\n{data}')
    return dict(parser.items('DEFAULT'))


def get_faults():
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
                        'bug_id': bug,
                        'buggy_commit': info['buggy_commit_id'].strip('"'),
                        'fixed_commit': info['fixed_commit_id'].strip('"'),
                        'test_file': info['test_file'].strip('"'),
                    }
                    yield fault
                break
        break


def evaluate_fault(fault):
    print(fault)
    if not os.path.isdir(fault['path']):
        subprocess.run(['git', 'clone', fault['github_url'],
                       fault['path']], capture_output=True, check=True)
    subprocess.run(['git', 'checkout', fault['fixed_commit']],
                   cwd=fault['path'], capture_output=True, check=True)
    rts = babelrts.BabelRTS(
        fault['path'], 'pysnooper', 'tests', [], ['python'])
    rts.rts()
    subprocess.run(['git', 'checkout', fault['buggy_commit']],
                   cwd=fault['path'], capture_output=True, check=True)
    rts.rts()
    exit()


def main():
    if not os.path.isdir(REPOS):
        os.makedirs(REPOS)
    faults = tuple(get_faults())
    for fault in faults:
        evaluate_fault(fault)


if __name__ == '__main__':
    main()
