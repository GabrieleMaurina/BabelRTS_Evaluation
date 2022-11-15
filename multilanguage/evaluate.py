#!/usr/bin/env python

from sys import path
path.append('../../BabelRTS')
from babelrts import BabelRTS
from os.path import isdir, join, basename
from glob import glob
from os import mkdir
from re import compile
from subprocess import run
from time import time
from statistics import mean
from simpleobject import simpleobject as so

N_REV = 30
TOT_REV = N_REV + 1

SUBJECTS_FOLDER = 'subjects'
RESULTS_FOLDER = 'results'
SUBJECT_NAME = compile(r'([^\/]+)\.git$')
REPOS_FOLDER = 'repos'

BABELRTS_FILE = '.babelrts'

def rc(cmd, cwd):
    return run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)

def init(subjects_file):
    print('***COLLECTING SUBJECTS DATA***')
    with open(subjects_file, 'r') as csv:
        table = [row.split(',') for row in csv.read().split('\n') if row]
    subjects = []
    for row in table:
        subject = so()
        subjects.append(subject)
        subject.url = row[0]
        subject.name = SUBJECT_NAME.search(subject.url)[1]
        subject.path = join(REPOS_FOLDER, subject.name)
        subject.test_folder = row[1]
        subject.source_folder = row[2]
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

def get_shas(subjects):
    print('***GETTING SHAS***')
    for subject in subjects:
        shas = rc(f'git --no-pager log --first-parent --pretty=tformat:"%H" --max-count={TOT_REV}', subject.path)
        if shas.returncode:
            raise Exception(f'Unable to get shas for {subject.url}')
        subject.shas = tuple(reversed(tuple(sha for sha in shas.stdout.split('\n') if sha)))

def get_loc_nfiles(subjects, languages):
    print('***GETTING LOC AND NFILES***')
    extensions = BabelRTS(languages=languages).get_dependency_extractor().get_extensions()
    for subject in subjects:
        subject.loc = subject.nfiles = 0
        for extension in extensions:
            subject.loc += int(rc(f'( find . -name "*.{extension}" -print0 | xargs -0 cat ) | wc -l', subject.path).stdout)
            subject.nfiles += int(rc(f'find . -name "*.{extension}" | wc -l', subject.path).stdout)

def run_babelrts(subjects, languages):
    print('***RUNNING BABELRTS***')
    for subject in subjects:
        print(f'Subject: {subject.name}')
        subject.times = []
        subject.reductions = []
        babelRTS = BabelRTS(subject.path, subject.source_folder, subject.test_folder, languages)
        first = True
        for sha in subject.shas:
            if rc(f'git checkout {sha}', subject.path).returncode:
                raise Exception('Unable to checkout sha {}'.format(sha))
            if first:
                first = False
            else:
                t = time()
                selected_tests = babelRTS.rts()
                t = time() - t
                subject.times.append(t)
                test_files = babelRTS.get_change_discoverer().get_test_files()
                reduction = (1 - len(selected_tests)/len(test_files)) if test_files else 1
                subject.reductions.append(reduction)
        subject.avg_time = mean(subject.times)
        subject.avg_reduction = mean(subject.reductions)

def save_results(subjects, languages):
    print('***SAVING RESULTS***')
    if not isdir(RESULTS_FOLDER):
        mkdir(RESULTS_FOLDER)
    with open(join(RESULTS_FOLDER, '_'.join(languages) + '_results.csv'), 'w') as out:
        out.write('subject,sha,loc,nfiles,reduction,time\n')
        for subject in subjects:
            out.write(f'{subject.name},{subject.shas[-1]},{subject.loc},{subject.nfiles},{subject.avg_reduction},{subject.avg_time}\n')

def main():
    for subjects_file in glob(join(SUBJECTS_FOLDER, '*_subjects.csv')):
        languages = basename(subjects_file).split('_')[:-1]
        print(f'\n\n*****LANGUAGES:{"-".join(languages)}*****')
        subjects = init(subjects_file)
        clone_subjects(subjects)
        get_shas(subjects)
        get_loc_nfiles(subjects, languages)
        run_babelrts(subjects, languages)
        save_results(subjects, languages)

if __name__ == '__main__':
    main()
