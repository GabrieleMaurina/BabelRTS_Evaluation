from os.path import join
import pandas as pd

N_COMMITS = 11

def add_shas(repo, changes, k, delta, start):
    hashcodes = tuple(pd.read_csv(changes).hashcode)
    first = k * start - delta - 1
    commits = hashcodes[first:first+k*N_COMMITS:k]
    repo.shas = commits
