#!/usr/bin/env python

from subprocess import run
from withcd import cd
from re import compile
from os.path import isdir

JUNIT = compile(r'junit[\s\S]+?([45])')
JUNIT_VERSION = compile(r'<junit.version>([45]).+?<\/junit.version>')

REPOS = ('https://github.com/apache/commons-configuration.git',
    'https://github.com/apache/commons-collections.git',
    'https://github.com/apache/commons-cli.git',    
    'https://github.com/apache/commons-dbcp.git',
    'https://github.com/apache/commons-pool.git',
    'https://github.com/apache/commons-text.git',
    'https://github.com/apache/commons-fileupload.git',
    'https://github.com/apache/commons-io.git',
    'https://github.com/apache/commons-lang.git',
    'https://github.com/apache/commons-jxpath.git',
    'https://github.com/apache/commons-net.git',
    'https://github.com/apache/commons-validator.git',
    'https://github.com/brettwooldridge/HikariCP.git',
    'https://github.com/addthis/stream-lib.git')

REPOS_FOLDER = 'repos'

def rc(cmd):
    return run(cmd, shell=True, capture_output=True, text=True)

def junit5():
    with open('pom.xml', 'r') as pom:
        pom = pom.read()
        version = JUNIT_VERSION.search(pom)
        if version:
            return int(version.group(1)) == 5
        return int(JUNIT.search(pom).group(1)) == 5

def get_hash():
    return rc('git rev-parse HEAD').stdout[:-1]

def get_branch():
    HEAD_BRANCH = '  HEAD branch: '
    for line in rc('git remote show origin').stdout.split('\n'):
        if line.startswith(HEAD_BRANCH):
            return line.replace(HEAD_BRANCH,'')
    raise ValueError('Unable to determine main branch')

def main():
    if not isdir(REPOS_FOLDER):
        mkdir(REPOS_FOLDER)
    with cd(REPOS_FOLDER):
        for r in REPOS:
            name = r.rsplit('/',1)[-1].rsplit('.',1)[0]
            if not isdir(name):
                rc(f'git clone {r}')
            with cd(name):
                rc(f'git clean -fd ; git reset --hard ; git checkout {get_branch()} ; git pull')
                while junit5():
                    rc(f'git checkout HEAD~1')
                print(name, get_hash())

if __name__ == '__main__':
    main()
