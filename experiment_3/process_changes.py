from sys import argv
from matplotlib import pyplot as plt
from progressbar import progressbar
import pandas as pd

from utils.folder_manager import dump
import utils.subjects as subjects

WINDOW_LENGTH = 10


def plot_changes(subject, data):
    plt.plot(data[[subjects.JAVA, subjects.PYTHON, subjects.CPP]])
    plt.legend(['Java', 'Python', 'C++'])
    plt.savefig(subjects.CHANGES_PLOT[subject])


def all_changed(languages, row):
    java = subjects.JAVA not in languages or row[subjects.JAVA] > 0
    python = subjects.PYTHON not in languages or row[subjects.PYTHON] > 0
    cpp = subjects.CPP not in languages or row[subjects.CPP] > 0
    return java and python and cpp


def longest_changes(data, languages):
    best_start = 0
    best_length = 0
    start = 0
    for index, changed in data.apply(lambda row: all_changed(languages, row), axis=1).items():
        if changed:
            length = index - start + 1
            if length > best_length:
                best_start = start
                best_length = length
        else:
            start = index + 1
    return  data.iloc[best_start].hashcode, best_start, best_length


def groups_of(data, k):
    for i in range(k):
        groups = data.groupby((data.index + i) // k)
        aggregations = {
            'hashcode': ('hashcode', 'first'),
            subjects.JAVA: (subjects.JAVA, 'sum'),
            subjects.PYTHON: (subjects.PYTHON, 'sum'),
            subjects.CPP: (subjects.CPP, 'sum')
        }
        yield groups.agg(**aggregations), i


def compute_consecutives(subject, data, max_aggregation):
    consecutives = []
    for k in progressbar(range(1, max_aggregation + 1)):
        for group, delta in groups_of(data, k):
            hashcode, index, length = longest_changes(group, subjects.LANGUAGES[subject])
            consecutives.append((k, delta, index, length, hashcode))
    return consecutives


def save_consecutives(subject, consecutives):
    df = pd.DataFrame(consecutives, columns=['k', 'delta', 'start', 'length', 'hashcode'])
    df.to_csv(subjects.CONSECUTIVE_CHANGES[subject], index=False)


def find_best_window(data, languages):
    best_index = None
    best_score = -1
    best_hashcodes = None
    n = len(data) - WINDOW_LENGTH
    for i in progressbar(range(1, n)):
        window = data.iloc[i:i + WINDOW_LENGTH]
        score = window[languages].sum().min()
        if score > best_score:
            best_score = score
            best_index = i
            best_hashcodes = (data.iloc[i - 1].hashcode,) + tuple(window.hashcode)
    return best_index, best_score, best_hashcodes

def save_best_window(subject, best_window):
    data = {}
    data['index'] = int(best_window[0])
    data['score'] = int(best_window[1])
    data['hashcodes'] = best_window[2]
    dump(data, subjects.BEST_WINDOW[subject])


def load_changes_csv(subject):
    return pd.read_csv(subjects.CHANGES[subject])


def main(subject, max_aggregation):
    data = load_changes_csv(subject)
    plot_changes(subject, data)

    best_window = find_best_window(data, list(subjects.LANGUAGES[subject]))
    save_best_window(subject, best_window)

    consecutives = compute_consecutives(subject, data, max_aggregation)
    save_consecutives(subject, consecutives)


if __name__ == '__main__':
    subject = argv[1]
    max_aggregation = int(argv[2])
    main(subject, max_aggregation)
