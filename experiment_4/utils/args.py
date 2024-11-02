import argparse


def parse_args(name):
    parser = argparse.ArgumentParser(
        description=f'Evaluate babelrts on {name}')
    parser.add_argument('-s', '--sut', nargs='+',
                        default=(), help='Subject under test')
    parser.add_argument('-n', '--new-faults', action='store_true', default=False,
                        help='Only evaluate new faults')
    args = parser.parse_args()
    return args
