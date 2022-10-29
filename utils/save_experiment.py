from os.path import isdir, join
from os import mkdir
from json import dump
from statistics import mean
from csv import DictWriter
from simpleobject import simpleobject as so

DATA_JSON = 'data.json'
SUTS_CSV = 'suts.csv'
REVS_CSV = 'revs.csv'
RESULTS = 'results'

def div(a, b, c=1.0):
    return a/b if b else c

def get_rpaf(pp, p, all):
    p = set(p)
    pp = set(pp)
    all = set(all)
    tp = len(p & pp)
    tn = len(all - p - pp)
    fp = len(pp - p)
    fn = len(p - pp)
    p = len(p)
    pp = len(pp)
    all = len(all)
    return so(recall = div(tp, p), precision=div(tp, pp), accuracy=div(tp + tn, all), f1score=div(tp + tp, tp + tp + fp + fn))

def save_experiment(experiment):
    if not isdir(RESULTS):
        mkdir(RESULTS)
    name = experiment.name.lower()
    with open(join(RESULTS, f'{name}_{DATA_JSON}'), 'w') as OUT:
        dump(experiment, OUT, indent='  ')
    suts = []
    revs = []
    for r in experiment.repos:
        if 'loc' not in r.commits[0] : continue
        r_revs = []
        for commit in r.commits:
            row = so()
            row.sut = r.name
            row.hash = commit.hash
            row.files = commit.files
            row.loc = commit.loc
            row.changed = len(commit.babelrts.changed)
            row.changed_per = div(len(commit.babelrts.changed), commit.files)
            row.all_tests = len(commit.all.tests)
            for tool, res in commit.tools.items():
                row[tool + '_tests'] = len(res.tests)
            row.babelrts_tests = len(commit.babelrts.tests)
            for tool, res in commit.tools.items():
                rpaf = get_rpaf(commit.babelrts.tests, res.tests, commit.all.tests)
                for k, v in rpaf.items():
                    row[f'{k}_wrt_{tool}'] = v
            row.all_duration = commit.all.duration
            for tool, res in commit.tools.items():
                row[tool + '_duration'] = res.duration
            row.babelrts_duration = commit.babelrts.duration
            for tool, res in commit.tools.items():
                row[tool + '_tr'] = div(commit.all.duration - res.duration, commit.all.duration)
            row.babelrts_tr = div(commit.all.duration - commit.babelrts.duration, commit.all.duration)
            for tool, res in commit.tools.items():
                row[tool + '_tsr'] = div(len(commit.all.tests) - len(res.tests), len(commit.all.tests))
            row.babelrts_tsr = div(len(commit.all.tests) - len(commit.babelrts.tests), len(commit.all.tests))
            r_revs.append(row)
        suts.append(mean_so(r_revs))
        revs.extend(r_revs)
    write_csv(f'{name}_{SUTS_CSV}', suts)
    write_csv(f'{name}_{REVS_CSV}', revs)

def mean_so(data):
    return so({key: data[0][key] if isinstance(data[0][key], str) else mean(row[key] for row in data) for key in data[0]})

def write_csv(name, data):
    with open(join(RESULTS, name), 'w', newline='') as out:
        writer = DictWriter(out, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)
