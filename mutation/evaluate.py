#!/usr/bin/env python

from sys import path, argv
path.append('../../BabelRTS')
from babelrts import BabelRTS
from os.path import isdir, join, basename, relpath
from glob import glob
from os import mkdir, walk
from re import compile
from csv import DictReader
from simpleobject import simpleobject as so
from json import dump
from utils.java import Java
from utils.javascript import Javascript
from utils.python import Python
from utils.run_cmd import rc
from utils.deletion_mutation import delete_lines

N_REV = 1

SUBJECTS_FOLDER = 'subjects_short'
RESULTS_FOLDER = 'results'
SUBJECT_NAME = compile(r'([^\/]+)\.git$')
REPOS_FOLDER = 'repos'

LANGUAGES = so(
    java=Java,
    javascript=Javascript,
    python=Python)

SKIP = so(
    java=True,
    javascript=True,
    python=False
)

BABELRTS_FILE = '.babelrts'

EXCLUDED = ('node_modules',)

def init(subjects_file):
    print('***COLLECTING SUBJECTS DATA***')
    with open(subjects_file, 'r') as csv:
        reader = DictReader(csv)
        table = tuple(so(row) for row in reader)
    subjects = []
    for row in table:
        subject = so()
        subjects.append(subject)
        subject.url = row.url
        subject.name = SUBJECT_NAME.search(subject.url)[1]
        subject.path = join(REPOS_FOLDER, subject.name)
        subject.test_folder = row.test_folder
        subject.source_folder = row.source_folder
        print(subject)
    return subjects

def get_branch(path):
    HEAD_BRANCH = '  HEAD branch: '
    for line in rc('git remote show origin', cwd=path).stdout.split('\n'):
        if line.startswith(HEAD_BRANCH):
            return line.replace(HEAD_BRANCH,'')
    raise ValueError('Unable to determine main branch')

def clone_subjects(subjects):
    print('***CLONING REPOS***')
    if not isdir(REPOS_FOLDER):
        mkdir(REPOS_FOLDER)
    for subject in subjects:
        if not isdir(subject.path):
            print(f'Cloning: {subject.url}')
            rc(f'git clone {subject.url}', REPOS_FOLDER)
        subject.branch = get_branch(subject.path)
        rc(f'rm {BABELRTS_FILE} ; git clean -fd ; git reset --hard ; git checkout {subject.branch} ; git pull', subject.path)

def get_shas(subjects, n_revs):
    print('***GETTING SHAS***')
    for subject in subjects:
        shas = rc(f'git --no-pager log --first-parent --pretty=tformat:"%H" --max-count={n_revs}', subject.path)
        if shas.returncode:
            raise Exception(f'Unable to get shas for {subject.url}')
        subject.shas = tuple(reversed(tuple(sha for sha in shas.stdout.split('\n') if sha)))

def get_loc(root, files):
    if files:
        K = 100
        files = tuple(files)
        partition = (files[i:i+K] for i in range(0, len(files), K))
        def loc(paths):
            return int(rc(f'wc -l ' + ' '.join(paths), root).stdout.split('\n')[-2].rsplit(' ', 1)[0])
        return sum(loc(paths) for paths in partition)
    else:
        return 0

def get_loc_nfiles(subject, babelRTS):
    all_files = babelRTS.get_change_discoverer().get_all_files()
    subject.loc = get_loc(subject.path, all_files)
    subject.nfiles = len(all_files)

def log(subject):
    values = []
    values.append(subject.mutants)
    values.append(subject.valid_mutants)
    values.append(subject.suite_killed)
    values.append(subject.babelrts_killed)
    values.append(subject.suite_failed)
    values.append(subject.babelrts_failed)
    print('\t'.join(str(v) for v in values))

def run(subjects, languages):
    print('***RUNNING***')
    language = LANGUAGES[languages[0]]()
    for subject in subjects:
        print(f'Subject: {subject.name}')
        subject.mutants = 0
        subject.valid_mutants = 0
        subject.suite_killed = 0
        subject.babelrts_killed = 0
        subject.suite_failed = 0
        subject.babelrts_failed = 0
        subject.missed = []
        language.set_project_folder(subject.path)
        language.set_test_folder(subject.test_folder)
        babelRTS = BabelRTS(subject.path, subject.source_folder, subject.test_folder, EXCLUDED, languages)
        for i, sha in enumerate(subject.shas):
            print(sha)
            if rc(f'git checkout {sha}', subject.path).returncode:
                raise Exception('Unable to checkout sha {}'.format(sha))
            language.init_repo()
            failures = language.test()
            if failures == 0:
                babelRTS.get_change_discoverer().clear_babelrts_data()
                babelRTS.get_change_discoverer().explore_codebase()
                if not i:
                    get_loc_nfiles(subject, babelRTS)
                babelRTS.get_dependency_extractor().generate_dependency_graph()
                source_files = babelRTS.get_change_discoverer().get_source_files()
                for changed_file, line in delete_lines(subject.path, source_files):
                    subject.mutants += 1
                    suite_failures = language.test()
                    if suite_failures is not None:
                        subject.valid_mutants += 1
                    if suite_failures:
                        subject.suite_killed += 1
                        subject.suite_failed += suite_failures
                        babelRTS.get_change_discoverer().set_changed_files({changed_file})
                        selected_tests = babelRTS.get_test_selector().select_tests()
                        babelrts_failures = None
                        if selected_tests:
                            babelrts_failures = language.test(selected_tests)
                            if babelrts_failures:
                                subject.babelrts_killed += 1
                                subject.babelrts_failed += babelrts_failures
                        if not selected_tests or not babelrts_failures or babelrts_failures != suite_failures:
                            missed = so()
                            subject.missed.append(missed)
                            missed.sha = sha
                            missed.changed_file = changed_file
                            missed.line = line
                            missed.suite_failed = suite_failures
                            missed.babelrts_failed = babelrts_failures
                            missed.selected_tests = tuple(selected_tests)\
                        log(subject)

def save_results(subjects, languages):
    print('***SAVING RESULTS***')
    if not isdir(RESULTS_FOLDER):
        mkdir(RESULTS_FOLDER)
    with open(join(RESULTS_FOLDER, '_'.join(languages) + '_results.csv'), 'w') as out:
        out.write('subject,sha,loc,nfiles,mutants,valid_mutants,suite_killed,babelrts_killed,suite_failed,babelrts_failed\n')
        for subject in subjects:
            values = []
            values.append(subject.name)
            values.append(subject.shas[-1])
            values.append(subject.loc)
            values.append(subject.nfiles)
            values.append(subject.mutants)
            values.append(subject.valid_mutants)
            values.append(subject.suite_killed)
            values.append(subject.babelrts_killed)
            values.append(subject.suite_failed)
            values.append(subject.babelrts_failed)
            out.write(','.join(str(v) for v in values) + '\n')
    with open(join(RESULTS_FOLDER, '_'.join(languages) + '_results.json'), 'w') as out:
        dump(subjects, out, indent=2)

def main():
    for subjects_file in sorted(glob(join(argv[1] if len(argv) > 1 else SUBJECTS_FOLDER, '*_subjects.csv'))):
        languages = basename(subjects_file).split('_')[:-1]
        if not SKIP[languages[0]]:
            print(f'\n\n*****LANGUAGES:{"-".join(languages)}*****')
            subjects = init(subjects_file)
            clone_subjects(subjects)
            get_shas(subjects, int(argv[2]) if len(argv) > 2 else N_REV)
            run(subjects, languages)
            save_results(subjects, languages)

if __name__ == '__main__':
    main()
