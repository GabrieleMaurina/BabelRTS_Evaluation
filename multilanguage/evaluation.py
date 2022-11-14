#!/usr/bin/env python

from sys import path
path.append('../../BabelRTS')
from babelrts import BabelRTS
from tabulate import tabulate
from os.path import isdir, isfile, join, dirname, realpath, basename
from glob import glob
from os import mkdir, popen
from re import compile
from subprocess import run, DEVNULL
from shutil import rmtree, copytree
from time import time
from collections import defaultdict
from json import dump
from numpy import mean

N_REV = 30

FOLDER = 'tmp'
WORK_FOLDER = join(dirname(realpath(__file__)),FOLDER)
REPOS_FOLDER = 'repos'
SHAS_FOLDER = 'shas'
TOT_REV = N_REV + 1
SUBJECT_FOLDER = compile(r'\/([\w\-\.]*)\.git')

SUB_DATA = {}

def rm(path):
	try: rmtree(path)
	except: pass

def init(subjects):
	print('\n***SUBJECTS***')
	with open(subjects, 'r') as subjects:
		subjects = [subject.split(',') for subject in subjects.read().split('\n') if s]
    subjects = [(url, SUBJECT_FOLDER.search(url)[1], sha, tf, sf) for url, sha, tf, sf in subjects]
    subjects = [(url, name, join(REPOS_FOLDER, name), join(SHAS_FOLDER, f'{name}.txt'), sha, tf, sf) for url, name, sha, tf, sf in subjects]
    print(tabulate(subjects))
    return subjects

def clone_subjects():
	if not isdir(REPOS_FOLDER):
		mkdir(REPOS_FOLDER)

	if not isdir(SHAS_FOLDER):
		mkdir(SHAS_FOLDER)

	for url, name, folder, shas, sha, tf, sf in SUBJECTS:
		if not isdir(folder):
			print('Cloning: {}'.format(url))
			if run(['git', 'clone', url], cwd=REPOS_FOLDER, stdout=DEVNULL, stderr=DEVNULL).returncode:
				raise Exception('Unable to clone repo {}'.format(url))
	print('{} subjects cloned'.format(len(SUBJECTS)))

def get_shas():
	for url, name, folder, shas, sha, tf, sf in SUBJECTS:
		if not isfile(shas):
			print('Getting shas for {}'.format(url))
			if sha:
				if run(['git', 'checkout', sha], cwd=folder, stdout=DEVNULL, stderr=DEVNULL).returncode:
					raise Exception('Unable to checkout sha {}'.format(sha))
			hashes = run(['git', 'log', '--pretty=tformat:"%H"', '--max-count={}'.format(TOT_REV)], cwd=folder, capture_output=True, text=True)
			if hashes.returncode:
				raise Exception('Unable to get shas for {}'.format(url))
			hashes = reversed(hashes.stdout.replace('"', '').splitlines())
			with open(shas, 'w') as output:
				output.write('\n'.join(hashes))

	print('{} shas per subject acquired'.format(N_REV))

def get_loc_nfiles():
	exts = lang_profiles[LANG][0]
	loc = nfiles = 0
	for ext in exts:
		loc += int(popen('( find ./{}/ -name "*.{}" -print0 | xargs -0 cat ) | wc -l'.format(FOLDER, ext)).read())
		nfiles += int(popen('find ./{}/ -name "*.{}" | wc -l'.format(FOLDER, ext)).read())
	return loc, nfiles

def run_babelrts():
	print('***RUNNING BABELRTS***')
	subjects = defaultdict(list)
	for url, name, folder, shas, sha, tf, sf in SUBJECTS:
		print('Subject: {}'.format(name))
		rm(WORK_FOLDER)
		copytree(folder, WORK_FOLDER, symlinks=True)
		with open(shas, 'r') as shas:
			shas = shas.read().splitlines()
		SUB_DATA[name] = [shas[-1], *get_loc_nfiles()]
		first = True
		for sha in shas:
			if run(['git', 'checkout', sha], cwd=WORK_FOLDER, stdout=DEVNULL, stderr=DEVNULL).returncode:
				raise Exception('Unable to checkout sha {}'.format(sha))
			if first:
				first = False
			else:
				t = time()
				selected, dependencies, changed, new_hashes, test_files, source_files = rts(LANG, WORK_FOLDER, tf, sf)
				t = time()-t
				save_jsons(WORK_FOLDER, selected, dependencies, changed, new_hashes)
				reduction = (1 - len(selected)/len(test_files)) if test_files else -1
				if reduction >= 0:
					subjects[name].append((reduction, t))

	rm(WORK_FOLDER)
	subjects = [[k] + SUB_DATA[k] + list(mean(v, axis=0)) for k,v in subjects.items()]
	return subjects

def output(subjects):
	print('***RESULTS***')
	print(tabulate(subjects))
	with open(RESULTS, 'w') as out:
		out.write('\n'.join(','.join(str(v) for v in l) for l in subjects) + '\n')
	#with open('results.json', 'w') as out:
	#	dump(subjects, out)

def main():
    for subjects in glob('*_subjects.csv'):
        subjects = basename(subjects)
        languages = subjects.split('_')[:-1]
        print(f'***LANGUAGES:{"-".join(languages)}***')
        subjects = init(subjects)
        clone_subjects(subjects)
        get_shas(subjects)
        results = run_babelrts(subjects)
        output(results)

if __name__ == '__main__':
	main()
