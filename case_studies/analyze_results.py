from json import load
from csv import DictWriter
from sys import argv

from utils import subjects as subjects


def load_results(subject, history):
    results = {}
    for run in subjects.RUNS[subject]:
        json = subjects.JSON[subject][run][history]
        with open(json, 'r') as f:
            results[run] = load(f)
    return results


def process_commit(commit, commits):

    all_commit = commits[subjects.ALL]
    others_keys = tuple(key for key in commits.keys() if key != subjects.ALL)
    others_names = {key: key[0].upper() for key in others_keys}

    A = set(all_commit['selected_tests'])
    O = {key: set(commits[key]['selected_tests']) for key in others_keys}

    commit['A'] = len(A)
    for key in others_keys:
        commit[others_names[key]] = len(O[key])

    OU = set().union(*O.values())
    commit['U'] = len(OU)

    A_D_OU = A - OU
    commit['A\\U'] = len(A_D_OU)

    OU_D_A = OU - A
    commit['U\\A'] = len(OU_D_A)

    if len(OU_D_A) > 0:
        for t in OU_D_A:
            print(t)
        exit(0)

    commit['ilt'] = all_commit['tests']['all']['ilt']
    commit['iltc'] = all_commit['tests']['all']['iltc']
    commit['iltco'] = all_commit['tests']['all']['iltco']

    commit['A_Time'] = all_commit['analysis_time']

    commit['U_Time'] = 0
    for key in others_keys:
        commit[f'{others_names[key]}_time'] = commits[key]['analysis_time']
        commit['U_Time'] += commits[key]['analysis_time']


def aggregate_results(subject, results):
    aggregated_results = []
    commits = {run: results[run]['commits'] for run in subjects.RUNS[subject]}
    for i in range(len(results[subjects.ALL]['commits'])):
        shas = tuple(commits[run][i]['sha'] for run in subjects.RUNS[subject])
        if any(sha != shas[0] for sha in shas):
            raise ValueError(f'Commits do not match: {i}, {shas}')
        commit = {'sha': shas[0]}
        aggregated_results.append(commit)
        process_commit(commit, {run: commits[run][i] for run in subjects.RUNS[subject]})
    return aggregated_results


def save_csv(subject, history, aggregated_results):
    with open(subjects.OUTPUT[subject][history], 'w', newline='') as f:
        writer = DictWriter(f, fieldnames=aggregated_results[0].keys())
        writer.writeheader()
        writer.writerows(aggregated_results)


def compute_stats(subject, history, aggregated_results):
    unsafe = 0
    faster = 0
    wrong_iltco = []
    for commit in aggregated_results:
        if commit['A\\U'] > 0:
            unsafe += 1
        if commit['A_Time'] < commit['U_Time']:
            faster += 1
        if commit['A\\U'] != commit['iltco']:
            wrong_iltco.append(commit)
    with open(subjects.STATS[subject][history], 'w') as out:
        out.write(f'Unsafe: {unsafe}/{len(aggregated_results)}\n')
        out.write(f'Faster: {faster}/{len(aggregated_results)}\n')
        if wrong_iltco:
            out.write(f'A\\U != iltco : {len(wrong_iltco)}\n')
            for commit in wrong_iltco:
                out.write(commit['sha'])
                out.write(',')
                out.write(str(commit['A\\U']))
                out.write(',')
                out.write(str(commit['iltco']))
                out.write('\n')


def main(subject, history):
    results = load_results(subject, history)
    aggregated_results = aggregate_results(subject, results)
    compute_stats(subject, history, aggregated_results)
    save_csv(subject, history, aggregated_results)


if __name__ == '__main__':
    subject = argv[1]
    history = len(argv) > 2 and argv[2] == 'history'
    main(subject, history)
