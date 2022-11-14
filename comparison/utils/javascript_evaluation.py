from re import compile as recmp
from os.path import join, relpath
from simpleobject import simpleobject as so
from utils.run_cmd import rc

def build_javascript_project():
    rc('npm i --force')

def run_jest_tests(test_folder, hash=None):
    option = f'--changedSince {hash}' if hash else ''
    selected_tests = sorted(tuple(join(test_folder, relpath(path, test_folder)) for path in rc(f'jest {option} --listTests')[1].split('\n') if path and (path.endswith('js') or path.endswith('ts')) and not relpath(path, test_folder).startswith('..')))
    duration = rc(f'jest {option}')[3]
    return so(tests=selected_tests, duration=duration)

def run_babelrts_javascript_tests(selected_tests):
    rc(f'jest {" ".join(selected_tests)}')
