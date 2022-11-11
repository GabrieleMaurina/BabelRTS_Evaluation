from re import compile as recmp
from os.path import isfile
from simpleobject import simpleobject as so
from utils.run_cmd import rc

PYTEST_TESTS = recmp(r'(\S+\.py).+\[[ 0-9]{3}%\]\n')
PYTEST_COV = '.coverage'

def collect_pytest_tests(test_folder, res):
    selected_tests = tuple(PYTEST_TESTS.findall(res[1]))
    duration = res[3]
    return so(tests=sorted(selected_tests), duration=duration)

def run_pytest_tests(test_folder):
    res = rc(f'python3.9 -m pytest {test_folder}')
    return collect_pytest_tests(test_folder, res)

def run_pytestrts_tests(test_folder, hash):
    res = None
    not_first = isfile(PYTEST_COV)
    if not_first:
        res = rc(f'python3.9 -m pytest --rts --rts-coverage-db={PYTEST_COV} --rts-from-commit={hash} {test_folder}')
        res = collect_pytest_tests(test_folder, res)
    cov = rc(f'python3.9 -m pytest --cov={test_folder}')
    if not_first:
        res.duration += cov[3]
    return res

def run_babelrts_python_tests(selected_tests):
    rc(f'python3.9 -m pytest {" ".join(selected_tests)}')
