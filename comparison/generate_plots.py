#!/usr/bin/env python

from os.path import join, basename, isdir
from os import mkdir
from glob import glob
import matplotlib.pyplot as plt
from csv import DictReader
from simpleobject import simpleobject as so

RESULTS_FOLDER = 'results'
PLOTS_FOLDER = 'plots'

def add_vetically(metric, table, data):
    keys = tuple((key, key.split('_')[-1].capitalize()) for key in table[0].keys() if key.startswith(metric))
    for key, name in keys:
        data[metric][name] = tuple(float(row[key]) for row in table)

def add_horizontally(metric, table, data, language):
    keys = tuple((key, key.split('_')[0].capitalize()) for key in table[0].keys() if key.endswith(metric))
    values = {}
    for key, name in keys:
        values[name] = tuple(float(row[key]) for row in table)
    data[language + ' ' + metric.capitalize()] = values

def collect_data():
    data = so()
    data.loc = {}
    data.nfiles = {}
    data.changed = {}
    data.changed_per = {}
    data.recall = {}
    data.precision = {}
    data.accuracy = {}
    data.f1score = {}
    for results_file in glob(join(RESULTS_FOLDER, '*_suts.csv')):
        language = basename(results_file).split('_')[0].capitalize()
        with open(results_file, newline='') as csv:
            reader = DictReader(csv)
            table = tuple(so(row) for row in reader)
        data.loc[language] = tuple(float(row['loc']) for row in table)
        data.nfiles[language] = tuple(float(row['files']) for row in table)
        data.changed[language] = tuple(float(row['changed']) for row in table)
        data.changed_per[language] = tuple(float(row['changed_per']) for row in table)
        add_vetically('recall', table, data)
        add_vetically('precision', table, data)
        add_vetically('accuracy', table, data)
        add_vetically('f1score', table, data)
        add_horizontally('tests', table, data, language)
        add_horizontally('duration', table, data, language)
        add_horizontally('tr', table, data, language)
        add_horizontally('tsr', table, data, language)
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
    save_plot(data.loc, 'Lines Of Code')
    save_plot(data.nfiles, 'Source Files')
    save_plot(data.changed, 'Changed Files')
    save_plot(data.changed_per, 'Changed Files (%)')
    save_plot(data.recall, 'Recall')
    save_plot(data.precision, 'Precision')
    save_plot(data.accuracy, 'Accuracy')
    save_plot(data.f1score, 'F1 Score')
    for key in data.keys():
         if ' ' in key:
             save_plot(data[key], key)

if __name__ == '__main__':
    main()
