#!/usr/bin/env python

from sys import path
path.append('../')
from plot_utils import plot
from os.path import join, basename
from glob import glob
from simpleobject import simpleobject as so
from collections import defaultdict

RESULTS_FOLDER = 'results'
MUTATION_CSV = 'mutation.csv'

def collect_data():
    data = so()
    for results_file in sorted(glob(join(RESULTS_FOLDER, '*_results.csv'))):
        languages = basename(results_file).split('_')[:-1]
        name = languages[0].capitalize()
        language = so()
        data[name] = language
        table = plot.read_csv(results_file)
        language.loc = sum(int(row.loc) for row in table)
        language.nfiles = sum(int(row.nfiles) for row in table)
        language.mutants = sum(int(row.mutants) for row in table)
        language.valid_mutants = sum(int(row.valid_mutants) for row in table)
        language.suite_killed = sum(int(row.suite_killed) for row in table)
        language.babelrts_killed = sum(int(row.babelrts_killed) for row in table)
        language.killed_ratio = language.babelrts_killed / language.suite_killed
        language.suite_failed = sum(int(row.suite_failed) for row in table)
        language.babelrts_failed = sum(int(row.babelrts_failed) for row in table)
        language.failed_ratio = language.babelrts_failed / language.suite_failed
    return data

def save_data(data):
    with open(join(RESULTS_FOLDER, MUTATION_CSV), 'w') as out:
        keys = next(iter(data.values())).keys()
        formatted_keys = (' '.join(v.capitalize() for v in key.split('_')).replace('Ratio', '%') for key in keys)
        out.write('Language,')
        out.write(','.join(formatted_keys))
        out.write('\n')
        tot = defaultdict(int)
        for language, values in data.items():
            out.write(language + ',')
            out.write(','.join(str(values[key]) for key in keys))
            out.write('\n')
            for key in keys:
                tot[key] += values[key]
        tot = so(tot)
        tot.killed_ratio = tot.babelrts_killed / tot.suite_killed
        tot.failed_ratio = tot.babelrts_failed / tot.suite_failed
        out.write('Total,')
        out.write(','.join(str(tot[key]) for key in keys))
        out.write('\n')

def main():
    data = collect_data()
    save_data(data)

if __name__ == '__main__':
    main()
