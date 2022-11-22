#!/usr/bin/env python

from sys import path, argv
path.append('../../BabelRTS')
from babelrts import BabelRTS
from os.path import isdir, join, basename
from glob import glob
from os import mkdir
from re import compile
from subprocess import run
from time import time
from statistics import mean
from csv import DictReader
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

def count_dependencies(babelRTS):
    deps = 0
    ild = 0
    dependency_graph = babelRTS.get_dependency_extractor().get_dependency_graph()
    for file, dependencies in dependency_graph.items():
        ext1 = file.rsplit('.',1)[-1]
        for dependency in dependencies:
            deps += 1
            ext2 = dependency.rsplit('.',1)[-1]
            if ext1 != ext2:
                ild += 1
    return deps, ild

def run_babelrts(subjects, languages):
    print('***RUNNING BABELRTS***')
    ild = len(languages) > 1
    for subject in subjects:
        print(f'Subject: {subject.name}')
        subject.times = []
        subject.reductions = []
        subject.changed = []
        if ild:
            subject.deps = []
            subject.ilds = []
        babelRTS = BabelRTS(subject.path, subject.source_folder, subject.test_folder, languages=languages)
        first = True
        for sha in subject.shas:
            if rc(f'git checkout {sha}', subject.path).returncode:
                raise Exception('Unable to checkout sha {}'.format(sha))
            t = time()
            selected_tests = babelRTS.rts()
            t = time() - t
            if first:
                first = False
            else:
                subject.times.append(t)
                test_files = babelRTS.get_change_discoverer().get_test_files()
                reduction = (1 - len(selected_tests)/len(test_files)) if test_files else 1
                subject.reductions.append(reduction)
                subject.changed.append(len(babelRTS.get_change_discoverer().get_changed_files()))
                if ild:
                    deps, ilds = count_dependencies(babelRTS)
                    subject.deps.append(deps)
                    subject.ilds.append(ilds)
        subject.avg_time = mean(subject.times)
        subject.avg_reduction = mean(subject.reductions)
        subject.avg_changed = mean(subject.changed)
        if ild:
            subject.avg_deps = mean(subject.deps)
            subject.avg_ilds = mean(subject.ilds)

def save_results(subjects, languages):
    print('***SAVING RESULTS***')
    ild = len(languages) > 1
    if not isdir(RESULTS_FOLDER):
        mkdir(RESULTS_FOLDER)
    with open(join(RESULTS_FOLDER, '_'.join(languages) + '_results.csv'), 'w') as out:
        out.write('subject,sha,loc,nfiles,changed,reduction,time')
        if ild:
            out.write(',deps,ilds\n')
        else:
            out.write('\n')
        for subject in subjects:
            out.write(f'{subject.name},{subject.shas[-1]},{subject.loc},{subject.nfiles},{subject.avg_changed},{subject.avg_reduction},{subject.avg_time}')
            if ild:
                out.write(f',{subject.avg_deps},{subject.avg_ilds}\n')
            else:
                out.write('\n')

def main():
    experiments = tuple(languages.lower().split('_') for languages in argv[1:])
    for subjects_file in glob(join(SUBJECTS_FOLDER, '*_subjects.csv')):
        languages = basename(subjects_file).split('_')[:-1]
        if not experiments or languages in experiments:
            print(f'\n\n*****LANGUAGES:{"-".join(languages)}*****')
            subjects = init(subjects_file)
            clone_subjects(subjects)
            get_shas(subjects)
            get_loc_nfiles(subjects, languages)
            run_babelrts(subjects, languages)
            save_results(subjects, languages)

if __name__ == '__main__':
    main()
