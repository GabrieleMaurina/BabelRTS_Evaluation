import glob
import matplotlib.pyplot as plt
import os
import os.path
import pandas


DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(DIR, 'results')
PLOTS = os.path.join(DIR, 'plots')


NUMBER_COLS = ['selection_time', 'test_suite_reduction',
               'n_sources', 'n_tests', 'loc']
COLORS = ['tab:blue', 'tab:green', 'tab:orange']


def load_results():
    results = []
    for file in glob.glob(os.path.join(RESULTS, '*_results.csv')):
        name = os.path.basename(file).rsplit('_', 1)[0]
        data = pandas.read_csv(file)
        results.append({
            'name': name,
            'data': data
        })
    results.sort(key=lambda x: x['name'])
    return results


def compute_metrics(results):
    for result in results:
        result['describe'] = result['data'].describe()
        tot_detected = result['data']['detected'].sum()
        tot_faults = len(result['data'])
        result['fault_detection_rate'] = round(tot_detected / tot_faults, 2)


def make_plot(data, title):
    plt.title('Mean ' + title.replace('_', ' ').title())
    plt.bar([d['name'] for d in data], [d['value']
            for d in data], color=COLORS)
    plt.savefig(os.path.join(PLOTS, f'{title}.png'))
    plt.close()


def make_plots(results):
    for col in NUMBER_COLS:
        data = []
        for result in results:
            name = result['name']
            value = result['describe'][col].loc['mean']
            data.append({
                'name': name,
                'value': value
            })
        make_plot(data, col)
    make_plot([{'name': r['name'], 'value': r['fault_detection_rate']}
               for r in results], 'fault_detection_rate')


def main():
    if not os.path.isdir(PLOTS):
        os.mkdir(PLOTS)
    results = load_results()
    compute_metrics(results)
    make_plots(results)


if __name__ == '__main__':
    main()
