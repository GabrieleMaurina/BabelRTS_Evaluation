from re import compile as recmp
from os.path import isfile
from time import time
from simpleobject import simpleobject as so
from babelrts import babelrts
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

def run_babelrts_python_tests(src, test, all_tests):
    if all_tests is None:
        return None
    t = time()
    selected_tests, dependencies, changed, new_hashes, test_files, source_files = babelrts.rts(('python',), '.', (test,), (src,))
    babelrts.save_jsons('.', selected_tests, dependencies, changed, new_hashes)
    selected_tests = tuple(path for path in selected_tests if path in all_tests)
    if selected_tests:
        rc(f'python3.9 -m pytest {" ".join(selected_tests)}')
    duration = time()-t
    return so(tests=sorted(selected_tests), duration=duration, dependencies=dependencies, changed=sorted(tuple(changed)), files=sorted(new_hashes.keys()))

