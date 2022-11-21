#!/usr/bin/env python

from sys import path
path.append('../')
from plot_utils import plot
from os.path import join, basename
from glob import glob
from simpleobject import simpleobject as so

RESULTS_FOLDER = 'results'

COLORS = so(
    erlang=plot.COLORS.green,
    go=plot.COLORS.red,
    groovy=plot.COLORS.purple,
    jruby=plot.COLORS.brown,
    kotlin=plot.COLORS.pink,
    ruby=plot.COLORS.olive,
    rust=plot.COLORS.cyan,
)
COLORS['c#'] = plot.COLORS.blue
COLORS['c++'] = plot.COLORS.orange

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
        table = plot.read_csv(results_file)
        data.loc[name] = tuple(int(row.loc) for row in table)
        data.nfiles[name] = tuple(int(row.nfiles) for row in table)
        data.changed[name] = tuple(float(row.changed) for row in table)
        data.reductions[name] = tuple(float(row.reduction) for row in table)
        data.times[name] = tuple(float(row.time) for row in table)
        if 'ild' in table[0]:
            data.ilds[name] = tuple(float(row.ild) for row in table)
    return data

def main():
    data = collect_data()
    plot.save_plot(data.loc, 'Lines of Code', COLORS)
    plot.save_plot(data.nfiles, 'Source Files', COLORS)
    plot.save_plot(data.changed, 'Changed Files', COLORS)
    plot.save_plot(data.reductions, 'Test Suite Reduction (%)', COLORS)
    plot.save_plot(data.times, 'Analysis Time (s)', COLORS)
    plot.save_plot(data.ilds, 'Inter Language Dependencies', COLORS)

if __name__ == '__main__':
    main()
