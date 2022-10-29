from re import compile as recmp
from time import time
from os.path import join, relpath
from simpleobject import simpleobject as so
from babelrts import babelrts
from utils.run_cmd import rc

def build_javascript_project():
    rc('npm i --force')

def run_jest_tests(test_folder, hash=None):
    option = f'--changedSince {hash}' if hash else ''
    selected_tests = sorted(tuple(join(test_folder, relpath(path, test_folder)) for path in rc(f'jest {option} --listTests')[1].split('\n') if path and (path.endswith('js') or path.endswith('ts')) and not relpath(path, test_folder).startswith('..')))
    duration = rc(f'jest {option}')[3]
    return so(tests=selected_tests, duration=duration)

def run_babelrts_javascript_tests(src, test, all_tests):
    if all_tests is None:
        return None
    t = time()
    selected_tests, dependencies, changed, new_hashes, test_files, source_files = babelrts.rts(('javascript','typescript'), '.', (test,), (src,), ('node_modules',))
    babelrts.save_jsons('.', selected_tests, dependencies, changed, new_hashes)
    selected_tests = tuple(path for path in selected_tests if path in all_tests)
    if selected_tests:
        rc(f'jest {" ".join(selected_tests)}')
    duration = time()-t
    return so(tests=sorted(selected_tests), duration=duration, dependencies=dependencies, changed=sorted(tuple(changed)), files=sorted(new_hashes.keys()))
