#!/usr/bin/env python

from os.path import join, basename, isdir
from os import mkdir
from glob import glob
import matplotlib.pyplot as plt
from csv import DictReader
from simpleobject import simpleobject as so

RESULTS_FOLDER = 'results'
PLOTS_FOLDER = 'plots'

def collect_data():
    data = so()
    data.loc = {}
    data.nfiles = {}
    data.changed = {}
    data.reductions = {}
    data.times = {}
    data.ilds = {}
    for results_file in glob(join(RESULTS_FOLDER, '*_results.csv')):
        languages = basename(results_file).split('_')[:-1]
        name = '\n'.join(language.capitalize() for language in languages)
        with open(results_file, 'r') as csv:
            reader = DictReader(csv)
            table = tuple(so(row) for row in reader)
        data.loc[name] = tuple(int(row.loc) for row in table)
        data.nfiles[name] = tuple(int(row.nfiles) for row in table)
        data.changed[name] = tuple(float(row.changed) for row in table)
        data.reductions[name] = tuple(float(row.reduction) for row in table)
        data.times[name] = tuple(float(row.time) for row in table)
        if 'ild' in table[0]:
            data.ilds[name] = tuple(float(row.ild) for row in table)
    return data

def save_plot(data, title, y_label=None):
    if not isdir(PLOTS_FOLDER):
        mkdir(PLOTS_FOLDER)
    file_name = title.lower().replace(' ', '_')
    keys = tuple(sorted(data.keys()))
    values = tuple(data[key] for key in keys)
    figure = plt.figure()
    plt.boxplot(values)
    plt.xticks(range(1,len(keys)+1), keys)
    if y_label: plt.ylabel(y_label)
    plt.title(title)
    figure.savefig(join(PLOTS_FOLDER, file_name) + '.pdf')

def main():
    data = collect_data()
    save_plot(data.loc, 'Lines of Code')
    save_plot(data.nfiles, 'Source Files')
    save_plot(data.changed, 'Changed Files')
    save_plot(data.reductions, 'Test Suite Reduction (%)')
    save_plot(data.times, 'Analysis Time (s)')
    save_plot(data.ilds, 'Inter Language Dependencies')

if __name__ == '__main__':
    main()
