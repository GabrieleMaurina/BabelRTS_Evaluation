from os.path import isdir, join
from os import mkdir
import matplotlib.pyplot as plt
from csv import DictReader
from textwrap import wrap
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
    cyan='tab:cyan',
    white='white',
    black='black',
)

PLOTS_FOLDER = 'plots'

def read_csv(path):
    with open(path, newline='') as csv:
        return tuple(so(row) for row in DictReader(csv) if not next(iter(row.values())).startswith('#'))

def get_color(label, colors):
    label = label.lower()
    sorted_colors = sorted(colors.items(), key=lambda v: len(v[0]), reverse=True)
    for key, color in sorted_colors:
        if label.startswith(key):
            return color
    for key, color in sorted_colors:
        if key in label:
            return color

def save_plot(data, title, colors, sorted_keys=False):
    if not isdir(PLOTS_FOLDER):
        mkdir(PLOTS_FOLDER)
    file_name = title.lower().replace(' ', '_')
    labels = tuple(sorted(data.keys()) if sorted_keys else data.keys())
    values = tuple(data[label] for label in labels)
    width = len(labels)*0.3 + 0.5
    plt.figure(figsize=(width,3))
    if max(map(max, values)) > 100 or min(map(min, values)) < -100:
        plt.yscale('log')
    plot = plt.boxplot(values, labels=labels, patch_artist=True, showfliers=False, widths=0.6)
    for label, box, median in zip(labels, plot['boxes'], plot['medians']):
        box.set_facecolor(get_color(label, colors))
        median.set_color(COLORS.black)
    plt.xticks(rotation=90)
    wrap_size = len(labels)*4
    plt.title('\n'.join(wrap(title, wrap_size, break_long_words=False)))
    plt.tight_layout(pad=0)
    plt.savefig(join(PLOTS_FOLDER, file_name) + '.pdf')
    plt.close()
