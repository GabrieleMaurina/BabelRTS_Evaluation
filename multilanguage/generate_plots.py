#!/usr/bin/env python

from os.path import join, basename, isdir
from os import mkdir
from glob import glob
import matplotlib.pyplot as plt

RESULTS_FOLDER = 'results'
PLOTS_FOLDER = 'plots'
REDUCTION = 'Test Suite Reduction'
TIME = 'Analysis Time'
REDUCTION_LABEL = 'Reduction %'
TIME_LABEL = 'Time (s)'

def collect_data():
	reductions = {}
	times = {}
	for results_file in glob(join(RESULTS_FOLDER, '*_results.csv')):
		languages = basename(results_file).split('_')[:-1]
		name = '-'.join(language.capitalize() for language in languages)
		with open(results_file, 'r') as csv:
			table = [row.split(',') for row in csv.read().split('\n') if row][1:]
		reductions[name] = tuple(float(row[4]) for row in table)
		times[name] = tuple(float(row[5]) for row in table)
	return reductions, times

def save_plot(data, title, y_label):
	if not isdir(PLOTS_FOLDER):
		mkdir(PLOTS_FOLDER)
	file_name = title.lower().replace(' ', '_')
	keys = tuple(sorted(data.keys()))
	values = tuple(data[key] for key in keys)
	figure = plt.figure()
	plt.boxplot(values)
	plt.xticks(range(1,len(keys)+1), keys)
	plt.ylabel(y_label)
	plt.title(title)
	figure.savefig(join(PLOTS_FOLDER, file_name) + '.pdf')

def main():
	reductions, times = collect_data()
	save_plot(reductions, REDUCTION, REDUCTION_LABEL)
	save_plot(times, TIME, TIME_LABEL)

if __name__ == '__main__':
    main()
