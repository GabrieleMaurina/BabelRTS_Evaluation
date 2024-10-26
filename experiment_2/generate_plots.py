#!/usr/bin/env python

from sys import path
path.append('../')
from plot_utils import plot
from os import mkdir
from os.path import join, basename, isdir
from glob import glob
from simpleobject import simpleobject as so
import statistics

RESULTS_FOLDER = 'results'
AGGREGATED = join(RESULTS_FOLDER, 'aggregated')

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

def div(a, b, c=0):
    return a / b if b else c

def collect_data():
    data = so()
    data.loc = {}
    data.nfiles = {}
    data.changed = {}
    data.reductions = {}
    data.times = {}
    data.deps = {}
    data.ilds = {}
    data.ilds_per = {}
    data.shas = {}
    for results_file in sorted(glob(join(RESULTS_FOLDER, '*_results.csv'))):
        languages = basename(results_file).split('_')[:-1]
        name = '\n'.join(language.capitalize() for language in languages)
        table = plot.read_csv(results_file)
        data.shas[name] = tuple(f'{row.subject},{row.sha[:6]}' for row in table)
        data.loc[name] = tuple(int(row.loc) for row in table)
        data.nfiles[name] = tuple(int(row.nfiles) for row in table)
        data.changed[name] = tuple(float(row.changed) for row in table)
        data.reductions[name] = tuple(float(row.reduction) for row in table)
        data.times[name] = tuple(float(row.time) for row in table)
        if 'ilds' in table[0]:
            data.deps[name] = tuple(float(row.deps) for row in table)
            data.ilds[name] = tuple(float(row.ilds) for row in table)
            data.ilds_per[name] = tuple(div(float(row.ilds), float(row.deps)) for row in table)
    return data

def save_all(data):
    if not isdir(AGGREGATED):
        mkdir(AGGREGATED)
    save_aggregated(data.loc, 'loc')
    save_aggregated(data.nfiles, 'nfiles')
    save_aggregated(data.times, 'times')
    save_aggregated(data.times, 'times_mean', mean=True)
    save_aggregated(data.changed, 'changed', percentage=True)
    save_aggregated(data.ilds, 'ilds')
    save_aggregated(data.ilds, 'ilds_mean', mean=True)
    save_aggregated(data.shas, 'shas')
    save_aggregated(data.reductions, 'reductions', percentage=True)
    save_aggregated(data.reductions, 'reductions_mean', mean=True, percentage=True)
    adjusted_times = so()
    for lang in data.loc.keys():
        adjusted_times[lang] = [time/loc if loc else 1 for loc, time in zip(data.loc[lang], data.times[lang])]
    save_aggregated(adjusted_times, 'adjusted_times')

def per(v, percentage):
    try:
        v = float(v)
    except ValueError:
        return v
    if percentage:
        v = round(v*100, 2)
    return str(v)

def save_aggregated(data, name, mean=False, percentage=False):
    keys = tuple(data.keys())
    values = tuple(data[key] for key in keys)
    langs = sorted([lang.replace('\n', '-') for lang in keys])
    with open(join(AGGREGATED, name + '.csv'), 'w') as out:
        out.write(','.join(langs) + '\n')
        if mean:
            out.write(','.join(per(statistics.mean(numbers), percentage) for numbers in values) + '\n')
        else:
            for numbers in zip(*values):
                out.write(','.join(per(v, percentage) for v in numbers) + '\n')

def main():
    data = collect_data()
    save_all(data)
    exit(0)
    plot.save_plot(data.loc, 'Lines of Code', COLORS)
    plot.save_plot(data.nfiles, 'Source Files', COLORS)
    plot.save_plot(data.changed, 'Changed Files', COLORS)
    plot.save_plot(data.reductions, 'Test Suite Reduction (%)', COLORS)
    plot.save_plot(data.times, 'Analysis Time (s)', COLORS)
    plot.save_plot(data.deps, 'File Dependencies', COLORS)
    plot.save_plot(data.ilds, 'Inter Language Dependencies', COLORS)
    plot.save_plot(data.ilds_per, 'Inter Language Dependencies (%)', COLORS)

if __name__ == '__main__':
    main()
