#!/usr/bin/env python

from json import load
from os.path import isdir, join
from traceback import print_exc
from time import time
from sys import argv, path
path.append('../BabelRTS')
from simpleobject import simpleobject as so
from withcd import cd
from utils.run_cmd import rc
from utils.java_evaluation import run_junit_tests, run_ekstazi_tests, run_hyrts_tests, run_babelrts_java_tests
from utils.python_evaluation import run_pytest_tests, run_pytestrts_tests, run_babelrts_python_tests
from utils.javascript_evaluation import run_jest_tests, run_babelrts_javascript_tests
from utils.save_experiment import save_experiment
from babelrts import BabelRTS



CONF_JSON = 'short.json'
REPOS = 'repos'
BABELRTS_FILE = '.babelrts'

def check_extension(name, extensions):
    if name:
        for ext in extensions:
            if name.endswith('.' + ext):
                return True
    return False

def n_changed(h1, h2, extensions):
    return sum(1 for path in rc(f'git --no-pager diff --name-only {h1} {h2}')[1].split('\n') if check_extension(path,extensions))

def get_commits(revs, changed_files, extensions):
    hashcodes = tuple(hash for hash in rc(f'git --no-pager log --first-parent --pretty=tformat:"%H"')[1].split() if hash)
    commits = [so(hash=hashcodes[0])]
    p = 1
    for i in range(revs):
        while n_changed(hashcodes[p], commits[-1].hash, extensions) < changed_files:
            p += 1
        commits.append(so(hash=hashcodes[p]))
    return list(reversed(commits))

def get_branch():
    HEAD_BRANCH = '  HEAD branch: '
    for line in rc('git remote show origin')[1].split('\n'):
        if line.startswith(HEAD_BRANCH):
            return line.replace(HEAD_BRANCH,'')
    raise ValueError('Unable to determine main branch')

def download_repos(experiment):
    print('*downloading*')
    if not isdir(REPOS):
        mkdir(REPOS)
    with cd(REPOS):
        for r in experiment.repos:
            print(r.name)
            if not isdir(r.name):
                rc(f'git clone {r.git}')
            with cd(r.name):
                r.branch = get_branch()
                rc(f'rm -rf {BABELRTS_FILE} ; git clean -fd ; git reset --hard ; git checkout {r.branch} ; git pull')
                try: rc(f'git checkout {r.starting_commit}')
                except Exception: pass
                r.commits = get_commits(experiment.revs, experiment.changed_files, experiment.extensions)

def preprocess_repos(experiment):
    if 'generated' not in experiment: experiment.generated = []
    if 'exclude' not in experiment: experiment.exclude = []
    for r in experiment.repos:
        r.git = r.url + '.git'
        r.name = r.url.rsplit('/',1)[-1]
        if 'src_folder' not in r: r.src_folder = experiment.src_folder
        if 'test_folder' not in r: r.test_folder = experiment.test_folder
    experiment.repos.sort(key=lambda r: r.name.lower())
    download_repos(experiment)

def get_changed_files(h1, h2):
    return sorted(tuple(path for path in rc(f'git --no-pager diff --name-only {h1} {h2}')[1].split('\n') if path))

def get_loc(files):
    if files:
        K = 100
        partition = (files[i:i+K] for i in range(0, len(files), K))
        def loc(paths):
            return int(rc(f'wc -l ' + ' '.join(paths))[1].split('\n')[-1].rsplit(' ', 1)[0])
        return sum(loc(paths) for paths in partition)
    else:
        return 0

def init_commit(commit):
    commit.changed = ()
    commit.git_hash = ''
    commit.files = 0
    commit.loc = 0

def process_repos(experiment):
    print('*processing*')
    build = globals().get(experiment.build, None) if 'build' in experiment else None
    run_all_tests = globals()[experiment.run_all_tests]
    tools = tuple((tool, globals()[func]) for tool, func in experiment.tools.items())
    run_babelrts_tests = globals()[experiment.run_babelrts_tests]
    for r in experiment.repos:
        print(r.name)
        with cd(join(REPOS,r.name)):
            babelRTS = BabelRTS('.', r.src_folder, r.test_folder, experiment.exclude, experiment.languages)
            for i, commit in enumerate(r.commits):
                print(commit.hash)
                init_commit(commit)
                try:
                    rc(f'git clean -fde {" -e ".join(experiment.generated + [BABELRTS_FILE,])} ; git reset --hard ; git checkout {commit.hash}')
                    if build: build()
                    commit.all = run_all_tests(r.test_folder)
                    commit.tools = so()
                    prev_hash = r.commits[i-1].hash if i else None
                    for tool, func in tools:
                        commit.tools[tool] = func(r.test_folder, hash=prev_hash)
                    run_babelrts(babelRTS, r, commit, run_babelrts_tests)
                    if i:
                        commit.changed = get_changed_files(r.commits[i-1].hash, commit.hash)
                        commit.git_hash = rc('git rev-parse HEAD')[1]
                        commit.files = len(commit.babelrts.files)
                        commit.loc = get_loc(commit.babelrts.files)
                except Exception as e:
                    print_exc()
                    commit.exception = str(e)
                del commit.babelrts.files
        r.commits.pop(0)
        save_experiment(experiment)

def run_babelrts(babelRTS, r, commit, run_babelrts_tests):
    if commit.all.tests is None:
        commit.babelrts = None
    else:
        t = time()
        selected_tests = babelRTS.rts()
        selected_tests = tuple(path for path in selected_tests if path in commit.all.tests)
        if selected_tests:
            run_babelrts_tests(selected_tests)
        duration = time()-t
        changed = babelRTS.get_change_discoverer().get_changed_files()
        dependency_graph = babelRTS.get_dependency_extractor().get_dependency_graph()
        files = babelRTS.get_change_discoverer().get_all_files()
        dependencies = {k: tuple(v) for k, v in dependency_graph.items()}
        commit.babelrts = so(tests=sorted(selected_tests), duration=duration, dependencies=dependencies, changed=sorted(changed), files=sorted(files))

def read_conf():
    conf_json = CONF_JSON if len(argv) < 2 else argv[1]
    with open(conf_json, 'r') as conf:
        conf = (so(experiment) for experiment in load(conf))
    return tuple(experiment for experiment in conf if not experiment.skip)

def main():
    conf = read_conf()
    for experiment in conf:
        print(f'***{experiment.name}***')
        preprocess_repos(experiment)
        process_repos(experiment)

if __name__ == '__main__':
    main()
