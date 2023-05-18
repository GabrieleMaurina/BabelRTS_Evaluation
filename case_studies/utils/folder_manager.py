from os import mkdir
from os.path import isdir, join
from re import compile as cmpre
from utils.run_cmd import rc
from simpleobject import simpleobject as so
from json import dump as dump_json

REPOS = 'repos'
RESULTS = 'results'
N_COMMITS = 1

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
    rows = rc(f'git --no-pager log --first-parent --pretty=tformat:"%H" -{N_COMMITS+1}', path).stdout.split('\n')
    shas = [row for row in reversed(rows) if row]
    return so(name=name, git=git, path=path, shas=shas)

def dump(obj, name):
    with open(join(RESULTS, name) + '.json', 'w') as out:
        dump_json(obj, out, indent=2)
