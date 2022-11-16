#!/usr/bin/env python

from os.path import join, basename, isdir
from os import mkdir
from glob import glob
import matplotlib.pyplot as plt

RESULTS_FOLDER = 'results'
PLOTS_FOLDER = 'plots'
LOC = 'Lines of Code'
NFILES = 'Source Files'
REDUCTION = 'Test Suite Reduction'
TIME = 'Analysis Time'
ILD = 'Inter Language Dependencies'
REDUCTION_LABEL = 'Reduction %'
TIME_LABEL = 'Time (s)'

def collect_data():
    loc = {}
    nfiles = {}
    reductions = {}
    times = {}
    ilds = {}
    for results_file in glob(join(RESULTS_FOLDER, '*_results.csv')):
        languages = basename(results_file).split('_')[:-1]
        name = '\n'.join(language.capitalize() for language in languages)
        with open(results_file, 'r') as csv:
            table = [row.split(',') for row in csv.read().split('\n') if row][1:]
        loc[name] = tuple(int(row[2]) for row in table)
        nfiles[name] = tuple(int(row[3]) for row in table)
        reductions[name] = tuple(float(row[4]) for row in table)
        times[name] = tuple(float(row[5]) for row in table)
        if len(table[0]) > 6:
            ilds[name] = tuple(float(row[6]) for row in table)
    return loc, nfiles, reductions, times, ilds

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
    loc, nfiles, reductions, times, ilds = collect_data()
    save_plot(loc, LOC)
    save_plot(nfiles, NFILES)
    save_plot(reductions, REDUCTION, REDUCTION_LABEL)
    save_plot(times, TIME, TIME_LABEL)
    save_plot(ilds, ILD)

if __name__ == '__main__':
    main()
