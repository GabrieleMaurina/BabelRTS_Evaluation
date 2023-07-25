from os.path import join
import pandas as pd

N_COMMITS = 11

RESULTS = 'results'
TENSORFLOW_CHANGES = join(RESULTS, 'tensorflow_changes.csv')


def add_shas(repo, starting_commit_index, step_size):
    hashcodes = tuple(pd.read_csv(TENSORFLOW_CHANGES).hashcode)
    commits = hashcodes[::step_size]
    commits = commits[starting_commit_index: starting_commit_index + N_COMMITS]
    repo.shas = commits
