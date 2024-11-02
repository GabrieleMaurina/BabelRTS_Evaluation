import os
import os.path
import pandas


def store_results(csv_file, sut, bug, detected, tot_time, test_suite_reduction, n_sources, n_tests, loc):
    if os.path.isfile(csv_file):
        results = pandas.read_csv(csv_file)
        results.loc[-1] = [sut, bug, detected,
                           tot_time, test_suite_reduction, n_sources, n_tests, loc]
        results.drop_duplicates(
            subset=['sut', 'bug'], keep='last', inplace=True)
        results.sort_values(['sut', 'bug'],
                            inplace=True, ignore_index=True)
    else:
        results = pandas.DataFrame({'sut': [sut],
                                    'bug': [bug],
                                    'detected': [detected],
                                    'selection_time': [tot_time],
                                    'test_suite_reduction': [test_suite_reduction],
                                    'n_sources': [n_sources],
                                    'n_tests': [n_tests],
                                    'loc': [loc]})
    results.to_csv(csv_file, index=False)


def get_already_evaluated(csv_file):
    already_evaluated = set()
    if os.path.isfile(csv_file):
        results = pandas.read_csv(csv_file)
        for row in results.itertuples():
            already_evaluated.add((row.sut, row.bug))
    return already_evaluated


def get_loc(path, *extensions):
    loc = 0
    for root, _, files in os.walk(path):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                with open(os.path.join(root, file), 'r') as f:
                    loc += sum(1 for line in f.readlines() if line.strip())
    return loc
