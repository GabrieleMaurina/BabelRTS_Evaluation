from os.path import join
from matplotlib import pyplot as plt
import pandas as pd

RESULTS = 'results'
TENSORFLOW_CHANGES = join(RESULTS, 'tensorflow_changes.csv')
CONSECUTIVE_CHANGES = join(RESULTS, 'consecutive_changes.csv')


def plot_changes(data):
    plt.plot(data[['java', 'python', 'cpp']])
    plt.legend(['Java', 'Python', 'C++'])
    plt.show()


def all_changed(row):
    return row.java > 0 and row.python > 0 and row.cpp > 0


def longest_changes(data):
    best_start = 0
    best_length = 0
    start = 0
    for index, changed in data.apply(all_changed, axis=1).items():
        if changed:
            length = index - start + 1
            if length > best_length:
                best_start = start
                best_length = length
        else:
            start = index + 1
    return best_start, best_length


def group_of(data, k):
    groups = data.groupby(data.index // k)
    aggregations = {
        'hashcode': ('hashcode', 'first'),
        'java': ('java', 'max'),
        'python': ('python', 'max'),
        'cpp': ('cpp', 'max')
    }
    return groups.agg(**aggregations)


def save_consecutives(consecutives):
    df = pd.DataFrame(consecutives, columns=['k', 'start', 'length'])
    df.to_csv(CONSECUTIVE_CHANGES, index=False)


def main():
    data = pd.read_csv(TENSORFLOW_CHANGES)
    # plot_changes(data)
    consecutives = []
    for k in range(1, 100):
        grouped = group_of(data, k)
        index, length = longest_changes(grouped)
        print(k, index, length)
        consecutives.append((k, index, length))

    save_consecutives(consecutives)


if __name__ == '__main__':
    main()
