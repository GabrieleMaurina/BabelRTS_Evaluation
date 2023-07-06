from os import mkdir
from os.path import isdir, join
from re import compile as cmpre
from utils.run_cmd import rc
from simpleobject import simpleobject as so
from json import dump as dump_json, load as load_json

REPOS = 'repos'
RESULTS = 'results'

REPO_NAME = cmpre(r'\/(\w+)\.git')

if not isdir(REPOS):
    mkdir(REPOS)

if not isdir(RESULTS):
    mkdir(RESULTS)


def get_repo(git):
    name = REPO_NAME.search(git).group(1)
    path = join(REPOS, name)
    if not isdir(path):
        rc(f'git clone {git}', REPOS)
    else:
        rc(f'git checkout master', path)
        rc(f'git pull', path)
    return so(name=name, git=git, path=path, shas=[])


def dump(obj, name):
    with open(join(RESULTS, name) + '.json', 'w') as out:
        dump_json(obj, out, indent=2)


def load(name):
    with open(join(RESULTS, name) + '.json', 'w') as file:
        return load_json(file)
