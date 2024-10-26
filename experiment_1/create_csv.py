import glob
import json
import os.path
import pandas


DIR = os.path.normpath(os.path.dirname(__file__))
RESULTS = os.path.join(DIR, 'results')
DATA_CSV = os.path.join(RESULTS, 'data.csv')
COLUMNS = ['language', 'project', 'version',
           'file', 'predicted', 'actual', 'babelrts_tsr', 'other_tsr', 'babelrts_tr', 'other_tr']

REPOS = {
    'commons-cli',
    'commons-configuration',
    'commons-dbcp',
    'commons-fileupload',
    'commons-jxpath',
    'commons-lang',
    'commons-net',
    'commons-text',
    'commons-validator',
    'lambda',
    'Augmentor',
    'backtrader',
    'boltons',
    'docker-py',
    'isort',
    'paramiko',
    'pyecharts',
    'python-prompt-toolkit',
    'pytube',
    'tflearn',
    'axios',
    'chroma.js',
    'mathjs',
    'openzeppelin-contracts',
    'react-digraph',
    'riot',
    'substance',
    'taiko',
    'videojs-contrib-hls',
    'vue'
}


def load_data():
    data = []
    for file in glob.iglob(os.path.join(RESULTS, '*.json')):
        with open(file, 'r') as f:
            data.append(json.load(f))
    return data


def iterate_data(data):
    for language_data in data:
        language = language_data['name']
        for repo in language_data['repos']:
            project = repo['name']
            if project not in REPOS:
                continue
            for version, commit in enumerate(repo['commits']):
                all_tests = commit['all']['tests']
                babelrts_tests = commit['babelrts']['tests']
                gt_tool = 'hyrts' if 'hyrts' in commit['tools'] else next(
                    iter(commit['tools']))
                gt_tests = commit['tools'][gt_tool]['tests']
                if all_tests:
                    babelrts_tsr = len(babelrts_tests) / len(all_tests)
                    gt_tsr = len(gt_tests) / len(all_tests)
                else:
                    babelrts_tsr = 0.0
                    gt_tsr = 0.0
                all_duration = commit['all']['duration']
                babelrts_duration = commit['babelrts']['duration']
                gt_duration = commit['tools'][gt_tool]['duration']
                if all_duration:
                    babelrts_tr = 1.0 - babelrts_duration / all_duration
                    gt_tr = 1.0 - gt_duration / all_duration
                else:
                    babelrts_tr = 0.0
                    gt_tr = 0.0
                for file in all_tests:
                    yield language, project, version, file, file in babelrts_tests, file in gt_tests, babelrts_tsr, gt_tsr, babelrts_tr, gt_tr


def main():
    data = load_data()
    data = list(iterate_data(data))
    data = pandas.DataFrame(data, columns=COLUMNS)
    data.sort_values(by=COLUMNS, inplace=True, ignore_index=True)
    data.to_csv(DATA_CSV, index=False, header=True)


if __name__ == '__main__':
    main()
