from os.path import isdir, join
from os import mkdir
import matplotlib.pyplot as plt
from csv import DictReader
from simpleobject import simpleobject as so

COLORS = so(
    blue='tab:blue',
    orange='tab:orange',
    green='tab:green',
    red='tab:red',
    purple='tab:purple',
    brown='tab:brown',
    pink='tab:pink',
    gray='tab:gray',
    olive='tab:olive',
    cyan='tab:cyan'
)

PLOTS_FOLDER = 'plots'

def read_csv(path):
    with open(path, newline='') as csv:
        return tuple(so(row) for row in DictReader(csv))

def get_color(label, colors):
    label = label.lower()
    for key, color in sorted(colors.items(), key=lambda v: len(v[0]), reverse=True):
        if key in label:
            return color

def save_plot(data, title, colors):
    if not isdir(PLOTS_FOLDER):
        mkdir(PLOTS_FOLDER)
    file_name = title.lower().replace(' ', '_')
    labels = tuple(sorted(data.keys()))
    values = tuple(data[label] for label in labels)
    width = max(3, len(labels)*0.6)
    figure = plt.figure(figsize=(width,3))
    if max(map(max, values)) > 100:
        plt.yscale('log')
    plot = plt.boxplot(values, labels=labels, patch_artist=True)
    for label, box in zip(labels, plot['boxes']):
        box.set_facecolor(get_color(label, colors))
    plt.title(title)
    plt.tight_layout()
    figure.savefig(join(PLOTS_FOLDER, file_name) + '.pdf')
