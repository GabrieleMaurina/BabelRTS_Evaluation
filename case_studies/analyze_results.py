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


def process_commit(commit, cpp_commit, python_commit, java_commit, all_commit):
    C = set(cpp_commit['selected_tests'])
    P = set(python_commit['selected_tests'])
    J = set(java_commit['selected_tests'])
    A = set(all_commit['selected_tests'])

    commit['C'] = len(C)
    commit['P'] = len(P)
    commit['J'] = len(J)
    commit['A'] = len(A)

    CUPUJ = (C | P | J)
    commit['CUPUJ'] = len(CUPUJ)

    A_D_CUPUJ = A - CUPUJ
    commit['A\(CUPUJ)'] = len(A_D_CUPUJ)

    CUPUJ_D_A = CUPUJ - A
    commit['(CUPUJ)\A'] = len(CUPUJ_D_A)

    C_D_A = C - A
    P_D_A = P - A
    J_D_A = J - A

    commit['C\A'] = len(C_D_A)
    commit['P\A'] = len(P_D_A)
    commit['J\A'] = len(J_D_A)

    commit['ilt'] = all_commit['tests']['all']['ilt']
    commit['iltc'] = all_commit['tests']['all']['iltc']
    commit['iltco'] = all_commit['tests']['all']['iltco']

    commit['C_Time'] = cpp_commit['analysis_time']
    commit['P_Time'] = python_commit['analysis_time']
    commit['J_Time'] = java_commit['analysis_time']
    commit['A_Time'] = all_commit['analysis_time']
    commit['CUPUJ_Time'] = cpp_commit['analysis_time'] + \
        python_commit['analysis_time'] + \
        java_commit['analysis_time']


def aggregate_results(subject, results):
    aggregate_results = []
    commits_data = tuple(results[run]['commits'] for run in subjects.RUNS[subject])
    for cpp_commit, python_commit, java_commit, all_commit in zip(*commits_data):
        shas = (cpp_commit['sha'], python_commit['sha'],
                java_commit['sha'], all_commit['sha'])
        if any(sha != shas[0] for sha in shas):
            raise ValueError(f'Commits do not match {shas}')
        commit = {'sha': shas[0]}
        aggregate_results.append(commit)
        process_commit(commit, cpp_commit, python_commit,
                       java_commit, all_commit)
    return aggregate_results


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
        if commit['A\(CUPUJ)'] > 0:
            unsafe += 1
        if commit['A_Time'] < commit['CUPUJ_Time']:
            faster += 1
        if commit['A\(CUPUJ)'] != commit['iltco']:
            wrong_iltco.append(commit)
    with open(subjects.STATS[subject][history], 'w') as out:
        out.write(f'Unsafe: {unsafe}/{len(aggregated_results)}\n')
        out.write(f'Faster: {faster}/{len(aggregated_results)}\n')
        if wrong_iltco:
            out.write(f'A\(CUPUJ) != iltco : {len(wrong_iltco)}\n')
            for commit in wrong_iltco:
                out.write(commit['sha'])
                out.write(',')
                out.write(str(commit['A\\(CUPUJ)']))
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
