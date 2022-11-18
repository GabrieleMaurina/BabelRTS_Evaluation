#!/usr/bin/env python

from sys import path
path.append('../../BabelRTS')
from babelrts import BabelRTS
from os.path import isdir, join, basename, relpath
from glob import glob
from os import mkdir, walk
from re import compile
from subprocess import run
from csv import DictReader
from simpleobject import simpleobject as so
from utils.java_evalutation import java_build_test
from utils.javascript_evalutation import javascript_build_test
from utils.python_evalutation import python_build_test

N_REV = 1

SUBJECTS_FOLDER = 'subjects'
RESULTS_FOLDER = 'results'
SUBJECT_NAME = compile(r'([^\/]+)\.git$')
REPOS_FOLDER = 'repos'

BUILD_TEST = so(
    java=java_build_test,
    javascript=javascript_build_test,
    python=python_build_test)

BABELRTS_FILE = '.babelrts'

EXCLUDE = ('node_modules',)

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
        shas = rc(f'git --no-pager log --first-parent --pretty=tformat:"%H" --max-count={N_REV}', subject.path)
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

def get_ild(babelRTS):
    ild = 0
    dependency_graph = babelRTS.get_dependency_extractor().get_dependency_graph()
    for file, dependencies in dependency_graph.items():
        ext1 = file.rsplit('.',1)[-1]
        for dependency in dependencies:
            ext2 = dependency.rsplit('.',1)[-1]
            if ext1 != ext2:
                ild += 1
    return ild

def delete_lines(path, extensions):
    for root, dirs, files in walk(path):
        dirs[:] = [dir for dir in dirs if dir not in EXCLUDE]
        for file in files:
            if file not in EXCLUDE:
                if '.' in file:
                    name, extension = file.rsplit('.', 1)
                    if name and extension and extension in extensions:
                        file_path = join(root, file)
                        file_relpath = relpath(file_path, path)
                        with open(file_path, 'r') as code:
                            code = code.read().split('\n')
                        for i in range(len(code)):
                            missing_line = (line for pos, line in enumerate(code) if pos != index)
                            with open(file_path, 'w') as out:
                                out.write('\n'.join(missing_line))
                            yield file_path
                        with open(file_path, 'w') as out:
                            out.write('\n'.join(code))

def run(subjects, languages):
    print('***RUNNING***')
    extensions = BabelRTS(languages=languages).get_dependency_extractor().get_extensions()
    build_test = BUILD_TEST[languages[0]]
    for subject in subjects:
        print(f'Subject: {subject.name}')
        subject.babelrts_failed = 0
        subject.suite_failed = 0
        subject.babelrts_killed = 0
        subject.suite_killed = 0
        babelRTS = BabelRTS(subject.path, subject.source_folder, subject.test_folder, exclude=EXCLUDE, languages=languages)
        for sha in subject.shas:
            if rc(f'git checkout {sha}', subject.path).returncode:
                raise Exception('Unable to checkout sha {}'.format(sha))
            failed_tests = build_test()
            if not failed_tests and failed_tests is not None:
                babelRTS.rts()
                for changed_file in delete_lines(subject.path, extensions):
                    failed_tests = build_test()
                    if failed_tests:
                        subject.suite_killed += 1
                        subject.suite_failed += len(failed_tests)
                        babelRTS.get_change_discoverer().set_changed_files({changed_file})
                        failed_tests = build_test(babelRTS.get_test_selector().selected_tests())
                        if failed_tests:
                            subject.babelrts_killed += 1
                            subject.babelrts_failed += len(failed_tests)

def save_results(subjects, languages):
    print('***SAVING RESULTS***')
    if not isdir(RESULTS_FOLDER):
        mkdir(RESULTS_FOLDER)
    with open(join(RESULTS_FOLDER, '_'.join(languages) + '_results.csv'), 'w') as out:
        out.write('subject,sha,loc,nfiles,babelrts_failed,suite_failed,babelrts_killed,babelrts_killed\n')
        for subject in subjects:
            out.write(f'{subject.name},{subject.shas[-1]},{subject.loc},{subject.nfiles},{subject.babelrts_failed},{subject.suite_failed},{subject.babelrts_killed},{subject.babelrts_killed}\n')

def main():
    for subjects_file in glob(join(SUBJECTS_FOLDER, '*_subjects.csv')):
        languages = basename(subjects_file).split('_')[:-1]
        print(f'\n\n*****LANGUAGES:{"-".join(languages)}*****')
        subjects = init(subjects_file)
        clone_subjects(subjects)
        get_shas(subjects)
        get_loc_nfiles(subjects, languages)
        run(subjects, languages)
        #save_results(subjects, languages)

if __name__ == '__main__':
    main()
