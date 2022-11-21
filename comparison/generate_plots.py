#!/usr/bin/env python

from sys import path
path.append('../')
from plot_utils import plot
from os.path import join, basename
from glob import glob
from simpleobject import simpleobject as so

RESULTS_FOLDER = 'results'

COLORS = so(
    babelrts=plot.COLORS.blue,
    ekstazi=plot.COLORS.orange,
    hyrts=plot.COLORS.green,
    jest=plot.COLORS.red,
    pytestrts=plot.COLORS.purple,
    all=plot.COLORS.brown,
    java=plot.COLORS.pink,
    javascript=plot.COLORS.olive,
    python=plot.COLORS.cyan,
)

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
        table = plot.read_csv(results_file)
        data.loc[language] = tuple(float(row.loc) for row in table)
        data.nfiles[language] = tuple(float(row.files) for row in table)
        data.changed[language] = tuple(float(row.changed) for row in table)
        data.changed_per[language] = tuple(float(row.changed_per) for row in table)
        add_vetically('recall', table, data)
        add_vetically('precision', table, data)
        add_vetically('accuracy', table, data)
        add_vetically('f1score', table, data)
        add_horizontally('tests', table, data, language)
        add_horizontally('duration', table, data, language)
        add_horizontally('tr', table, data, language)
        add_horizontally('tsr', table, data, language)
    return data

def main():
    data = collect_data()
    plot.save_plot(data.loc, 'Lines Of Code', COLORS)
    plot.save_plot(data.nfiles, 'Source Files', COLORS)
    plot.save_plot(data.changed, 'Changed Files', COLORS)
    plot.save_plot(data.changed_per, 'Changed Files (%)', COLORS)
    plot.save_plot(data.recall, 'Recall', COLORS)
    plot.save_plot(data.precision, 'Precision', COLORS)
    plot.save_plot(data.accuracy, 'Accuracy', COLORS)
    plot.save_plot(data.f1score, 'F1 Score', COLORS)
    for key in data.keys():
         if ' ' in key:
            plot.save_plot(data[key], key, COLORS)

if __name__ == '__main__':
    main()
