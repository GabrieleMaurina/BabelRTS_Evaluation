from os.path import join
from json import load
from csv import DictWriter


RESULTS = 'results'
CPP_RESULTS = join(RESULTS, 'tensorflow_c++.json')
PYTHON_RESULTS = join(RESULTS, 'tensorflow_python.json')
JAVA_RESULTS = join(RESULTS, 'tensorflow_java.json')
ALL_RESULTS = join(RESULTS, 'tensorflow_all.json')
OUTPUT_CSV = join(RESULTS, 'tensorflow.csv')

RUNS = ('cpp', 'python', 'java', 'all')


def load_results():
    results = {}
    with open(CPP_RESULTS, 'r') as f:
        results['cpp'] = load(f)
    with open(PYTHON_RESULTS, 'r') as f:
        results['python'] = load(f)
    with open(JAVA_RESULTS, 'r') as f:
        results['java'] = load(f)
    with open(ALL_RESULTS, 'r') as f:
        results['all'] = load(f)
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

    commit['C_Time'] = cpp_commit['analysis_time']
    commit['P_Time'] = python_commit['analysis_time']
    commit['J_Time'] = java_commit['analysis_time']
    commit['A_Time'] = all_commit['analysis_time']
    commit['CUPUJ_Time'] = cpp_commit['analysis_time'] + \
        python_commit['analysis_time'] + \
        java_commit['analysis_time']


def aggregate_results(results):
    aggregate_results = []
    commits_data = tuple(results[run]['commits'] for run in RUNS)
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


def save_csv(aggregated_results):
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = DictWriter(f, fieldnames=aggregated_results[0].keys())
        writer.writeheader()
        writer.writerows(aggregated_results)


def main():
    results = load_results()
    aggregated_results = aggregate_results(results)
    save_csv(aggregated_results)


if __name__ == '__main__':
    main()
