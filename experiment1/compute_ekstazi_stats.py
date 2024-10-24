import json
import os.path
import statistics
import utils.save_experiment

RESULTS = 'results'
JAVA_DATA = os.path.join(RESULTS, 'java_data.json')
EKSTAZI_STATS = os.path.join(RESULTS, 'ekstazi_stats.csv')


def main():
    with open(JAVA_DATA, 'r') as f:
        java_data = json.load(f)

    results = [('subject', 'recall', 'precision', 'accuracy', 'f1score')]

    for repo in java_data['repos']:
        stats = []
        for commit in repo['commits']:
            all = commit['all']['tests']
            ekstazi = commit['tools']['ekstazi']['tests']
            hyrts = commit['tools']['hyrts']['tests']
            stats.append(utils.save_experiment.get_rpaf(ekstazi, hyrts, all))
        r = statistics.mean((s['recall'] for s in stats))
        p = statistics.mean((s['precision'] for s in stats))
        a = statistics.mean((s['accuracy'] for s in stats))
        f = statistics.mean((s['f1score'] for s in stats))
        results.append((repo['name'], r, p, a, f))
    
    with open(EKSTAZI_STATS, 'w') as f:
        for row in results:
            f.write(','.join(map(str, row)) + '\n')


if __name__ == '__main__':
    main()
