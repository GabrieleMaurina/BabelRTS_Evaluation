import os.path
import pandas
import scipy.stats
import sklearn.metrics
import matplotlib.pyplot
import numpy


DIR = os.path.normpath(os.path.dirname(__file__))
RESULTS = os.path.join(DIR, 'results')
DATA_CSV = os.path.join(RESULTS, 'data.csv')
STATS_CSV = os.path.join(RESULTS, 'stats.csv')
RECALL_DISTRIBUTION_PDF = os.path.join(RESULTS, 'recall_distribution.pdf')
PRECISION_DISTRIBUTION_PDF = os.path.join(
    RESULTS, 'precision_distribution.pdf')


def compute_mann_whitney_u(data, babelrts_column, other_column):
    data = data.drop_duplicates(
        subset=['language', 'project', 'version'], ignore_index=True)
    langs = data['language'].unique()
    for lang in langs:
        lang_data = data[data['language'] == lang]
        stat, p = scipy.stats.mannwhitneyu(
            lang_data[babelrts_column], lang_data[other_column])
        yield lang, round(float(stat), 4), round(float(p), 4)


def compute_recall_precision_for_group(group):
    recall = sklearn.metrics.recall_score(
        group['actual'], group['predicted'], zero_division=1)
    precision = sklearn.metrics.precision_score(
        group['actual'], group['predicted'], zero_division=1)
    return pandas.Series({'recall': recall, 'precision': precision})


def compute_recall_precision(data, groupby_columns=['language', 'project', 'version']):
    return data.groupby(groupby_columns).apply(compute_recall_precision_for_group, include_groups=False).reset_index()


def compute_confidence_interval(data, column, confidence=0.95):
    langs = data['language'].unique()
    for lang in langs:
        lang_data = data[data['language'] == lang]
        n = len(lang_data)
        mean = lang_data[column].mean()
        std = lang_data[column].std()
        l, h = scipy.stats.t.interval(
            confidence=confidence, df=n - 1, loc=mean, scale=std / n ** 0.5)
        yield lang, round(float(mean), 4), round(float(std), 4), round(float(l), 4), round(float(h), 4)


def plot_density(data, column):
    langs = sorted(data['language'].unique())
    for lang in langs:
        lang_data = data[data['language'] == lang]
        kde = scipy.stats.gaussian_kde(lang_data[column])
        x = numpy.linspace(0, 1, 100)
        matplotlib.pyplot.plot(x, kde(x), linewidth=3.0, label=lang)


def plot_recall_precision(data):
    recall_precision = compute_recall_precision(data)
    matplotlib.pyplot.figure(figsize=(10, 5), dpi=300)
    matplotlib.pyplot.subplot(1, 2, 1)
    matplotlib.pyplot.xlabel('Recall')
    matplotlib.pyplot.ylabel('Density')
    matplotlib.pyplot.title('Recall Distribution')
    matplotlib.pyplot.ylim(top=6)
    plot_density(recall_precision, 'recall')
    matplotlib.pyplot.legend(loc="upper left")
    matplotlib.pyplot.subplot(1, 2, 2)
    matplotlib.pyplot.xlabel('Precision')
    matplotlib.pyplot.ylabel('Density')
    matplotlib.pyplot.title('Precision Distribution')
    matplotlib.pyplot.ylim(top=6)
    plot_density(recall_precision, 'precision')
    matplotlib.pyplot.legend(loc="upper left")
    matplotlib.pyplot.tight_layout()
    matplotlib.pyplot.savefig(RECALL_DISTRIBUTION_PDF)
    matplotlib.pyplot.close()


def main():
    data = pandas.read_csv(DATA_CSV)
    plot_recall_precision(data)
    recall_precision = compute_recall_precision(data, ['language', 'project'])
    with open(STATS_CSV, 'w') as file:
        def p(v):
            print(v)
            file.write(v + '\n')
        p('### Precision and Recall ###')
        p('metric,lang,mean,std,lower,upper')
        for lang, mean, std, l, h in compute_confidence_interval(recall_precision, 'precision'):
            p(f'precision,{lang},{mean},{std},{l},{h}')
        for lang, mean, std, l, h in compute_confidence_interval(recall_precision, 'recall'):
            p(f'recall,{lang},{mean},{std},{l},{h}')
        p('\n### Mann-Whitney U Test ###')
        p('metric,lang,stat,p_value')
        for lang, stat, p_value in compute_mann_whitney_u(data, 'babelrts_tr', 'other_tr'):
            p(f'tr,{lang},{stat},{p_value}')
        for lang, stat, p_value in compute_mann_whitney_u(data, 'babelrts_tsr', 'other_tsr'):
            p(f'tsr,{lang},{stat},{p_value}')


if __name__ == '__main__':
    main()
