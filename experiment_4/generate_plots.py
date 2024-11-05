import glob
import json
import matplotlib.pyplot as plt
import os
import os.path
import pandas


DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(DIR, 'results')
PLOTS = os.path.join(DIR, 'plots')
STATS_JSON = os.path.join(RESULTS, 'stats.json')


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
        result['describe'] = result['data'].describe().to_dict()
        tot_detected = result['data']['detected'].sum()
        tot_faults = len(result['data'])
        result['fault_detection_rate'] = round(tot_detected / tot_faults, 2)
        means = result['data'].groupby('sut')[NUMBER_COLS].mean().to_dict()
        result['means'] = {k: tuple(v.values()) for k, v in means.items()}
        del result['data']

    with open(STATS_JSON, 'w') as f:
        json.dump(results, f, indent=4)


def make_bar_plot(data, title):
    plt.title('Mean ' + title.replace('_', ' ').title())
    plt.bar([d['name'] for d in data], [d['value']
            for d in data], color=COLORS)
    plt.savefig(os.path.join(PLOTS, f'{title}_bar.pdf'))
    plt.close()


def make_box_plot(data, title):
    plt.title(title.replace('_', ' ').title())
    for i in range(len(data)):
        box = plt.boxplot(data[i]['value'], positions=[i],
                          widths=0.6, patch_artist=True, sym='')
        for patch in box['boxes']:
            patch.set_facecolor(COLORS[i])
        for median in box['medians']:
            median.set_color('black')
    plt.xticks(range(len(data)), [d['name'] for d in data])
    plt.savefig(os.path.join(PLOTS, f'{title}_box.pdf'))
    plt.close()


def make_plots(results):
    for col in NUMBER_COLS:
        data = []
        box_data = []
        for result in results:
            name = result['name']
            value = result['describe'][col]['mean']
            data.append({
                'name': name,
                'value': value
            })
            box_data.append({
                'name': name,
                'value': result['means'][col]
            })
        make_bar_plot(data, col)
        make_box_plot(box_data, col)
    make_bar_plot([{'name': r['name'], 'value': r['fault_detection_rate']}
                   for r in results], 'fault_detection_rate')


def main():
    if not os.path.isdir(PLOTS):
        os.mkdir(PLOTS)
    results = load_results()
    compute_metrics(results)
    make_plots(results)


if __name__ == '__main__':
    main()
