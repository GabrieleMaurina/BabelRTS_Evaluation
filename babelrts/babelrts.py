'''BabelRTS performs regression test selection. Given a codebase that has changed, it selects which tests should be executed. Find out more at https://github.com/GabrieleMaurina/babelRTS'''

from os import walk, makedirs
from os.path import join, exists, relpath, normpath, basename, dirname
from argparse import ArgumentParser as arg_par
from hashlib import sha1
from json import load, dump
from collections import deque
from collections.abc import Iterable
from sys import stdout, stderr
from babelrts.languages import language_implementations

__author__ = 'Gabriele Maurina'
__copyright__ = 'Copyright 2020, Gabriele Maurina'
__credits__ = ['Gabriele Maurina']
__license__ = 'MIT'
__version__ = '1.1.7'
__maintainer__ = 'Gabriele Maurina'
__email__ = 'gabrielemaurina95@gmail.com'
__status__ = 'Production'

FOLDER = '.babelrts'

def register_language_implementation(name, language_implementation):
    '''Add new language implementation.'''

    language_implementations[name] = language_implementation

def remove_language_implementation(name):
    '''Remove language implementation.'''

    del language_implementations[name]

def get_language_implementations():
    '''Return copy of language implementations dictionary.'''

    return dict(language_implementations)

def sha1_file(path):
    '''Return sha1 of file.'''

    with open(path, 'rb') as file:
        return sha1(file.read()).hexdigest()

def load_hashes(path):
    '''Load and return previously computed hashes if available.'''

    try:
        with open(join(path, FOLDER, 'hashes.json'), 'r') as hashes:
            return load(hashes)
    except:
        return {}

def babelrts_dir(path):
    '''Create babelrts folder (".babelrts").'''

    path = join(path, FOLDER)
    if not exists(path):
            try:
                makedirs(path)
            except: pass
    return path

def dump_json(path, name, obj):
    '''Save json object "obj" in directory "path" with filename "name".'''

    with open(join(babelrts_dir(path), name + '.json'), 'w') as file:
        dump(obj, file, indent=4, sort_keys=True)

def get_files(path, extensions, project_folder, exclude=()):
    '''Return all files under path that fit the profile.'''

    for root, dirs, names in walk(path):
        dirs[:] = [d for d in dirs if d[0] != '.' and d not in exclude]
        for name in names:
            file_path = relpath(join(root, name), project_folder)
            split = name.rsplit('.', 1)
            if len(split) == 2:
                name, extension = split
                if name and extension and extension in extensions:
                    yield file_path

def get_dependencies(patterns_actions, files, project_folder):
    '''Return dependencies.'''

    dependencies = {}
        for file_path in files:
            file = basename(file_path)
            folder_path = dirname(file_path)
            split = file.rsplit('.', 1)
            if len(split) == 2:
                name, extension = split
                if name and extension and extension in patterns_actions:
                    with open(file_path, 'r', encoding='unicode_escape') as content:
                        content = content.read()
                    deps = set()
                    for pattern, action in patterns_actions[extension]:
                        for match in pattern.findall(content):
                            new_deps = action(match, file_path, folder_path, project_folder, content)
                            if new_deps:
                                deps.update({value for value in (normpath(relpath(dependency, project_folder)) for dep in new_deps) if value!=file_path})
                    if deps:
                        dependencies[path] = tuple(deps)
    return dependencies

def dfs_changed(test, dependencies, changed):
    '''Return true if test depends on one or more files that have changed.'''

    neighbors = deque(dependencies.get(test, []))
    visited = set(test)
    while neighbors:
        neighbor = neighbors.pop()
        if neighbor not in visited:
            visited.add(neighbor)
            if neighbor in changed:
                return True
            elif neighbor in dependencies:
                neighbors.extend(dependencies[neighbor])
    return False

def select(tests, dependencies, changed):
    '''Select tests to be run.'''

    selected = set()
    for test in tests:
        if test in changed or dfs_changed(test, dependencies, changed):
            selected.add(test)
    return selected

def get_patterns_actions(languages):
    '''Gather patterns and actions.'''

    patterns_actions = {}

    def add(extension_pattern_action):
        extension = extension_pattern_action.extension
        pattern = extension_pattern_action.pattern
        action = extension_pattern_action.action
        if extension not in patterns_actions:
            patterns_actions[extension] = [(pattern, action)]
        else:
            patterns_actions[extension] += (pattern, action)

    def update(language_implementation):
        extensions_patterns_actions = language_implementation().get_extensions_patterns_actions()
        if extensions_patterns_actions:
            if isinstance(extensions_patterns_actions, Iterable):
                for extension_pattern_action in extensions_patterns_actions:
                    add(extension_pattern_action)
            else:
                add(extensions_patterns_actions)

    if languages:
        for language in languages:
            update(language_implementations[language.lower()])
    else:
        for language_implementation in language_implementations.values():
            update(language_implementation)

    return patterns_actions

def rts(languages, project_folder, test_folders, source_folders, exclude=()):
    '''Perform regression test selection.'''

    patterns_actions = get_patterns_actions(languages)
    extensions = patterns_actions.keys()

    test_files = {file for test_folder in test_folders for file in get_files(test_folder, extensions, project_folder, exclude)}
    source_files = test_files - {file for source_folder in source_folders for file in get_files(source_folder, extensions, project_folder, exclude)}
    all_files = test_files + source_files

    old_hashes = load_hashes(project_folder)
    new_hashes = {file:sha1_file(join(project_folder, file)) for file in all_files}

    changed = {file for file, hash in new_hashes.items() if file not in old_hashes or new_hashes[file] != old_hashes[file]}
    dependencies = get_dependencies(patterns_actions, all_files, project_folder)
    selected = select(test_files, dependencies, changed)

    return selected, dependencies, changed, new_hashes, test_files, source_files

def save_jsons(project_folder, selected, dependencies, changed, new_hashes):
    '''Store RTS data into .babelrts folder.'''

    dump_json(project_folder, 'selected', list(selected))
    dump_json(project_folder, 'dependencies',  dependencies)
    dump_json(project_folder, 'changed',  list(changed))
    dump_json(project_folder, 'hashes',  new_hashes)

def print_results_file(selected, output):
    '''Write results to file.'''

    for test_file in selected:
        print(test_file, file=output)

def print_results(selected, output):
    '''Write results to file "output", if it exists, otherwise to stdout.'''

    if output:
        with open(output, 'w') as output:
            print_results_file(selected, output)
    else:
        print_results_file(selected, stdout)

def log(selected, dependencies, changed, test_files, source_files):
    '''Print logging information.'''

    T = len(test_files)
    S = len(source_files)
    C = len(changed)
    D = sum(len(v) for v in dependencies.values())
    SE = len(selected)
    print('***BabelRTS results***\nTest files: {}\nSource files: {}\nChanged: {}\nDependencies: {}\nSelected: {}'.format(T, S, C, D, SE), file=stderr)

def run(languages, project_folder, test_folders, source_folders, verbose, output):
    '''Perform RTS, then store data and perform logging.'''

    selected, dependencies, changed, new_hashes, test_files, source_files = rts(languages, project_folder, test_folders, source_folders)

    save_jsons(project_folder, selected, dependencies, changed, new_hashes)

    if output != '': print_results(selected, output)

    if verbose: log(selected, dependencies, changed, test_files, source_files)

def parse_args():
    '''Parse the arguments and return an object containing all settings.'''

    parser = arg_par(prog= 'python -m babelrts.babelrts', description='BabelRTS v{} : regression test selection. Given a codebase that has changed, it selects which tests should be executed. Find out more at https://github.com/GabrieleMaurina/babelRTS'.format(__version__))
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('-l', metavar='<languages>', nargs='+', help='set one or more languages (default all)')
    parser.add_argument('-p', metavar='<project folder>', default='.', help='set project folder (default "current working directory")')
    parser.add_argument('-t', metavar='<test folder>', nargs='+', default=[''], help='set one or more test folders relative to <project folder> (default same as <project folder>)')
    parser.add_argument('-s', metavar='<source folder>', nargs='+', default=[''], help='set one or more source folders relative to <project folder> (default same as <project folder>)')
    parser.add_argument('-o', metavar='<output>', nargs='?', default='', help='set output file (default "stdout")')
    args = parser.parse_args()
    return args

def main():
    '''Parse arguments and perform regression test selection.'''
    args = parse_args()
    run(args.l, args.p, args.t, args.s, args.verbose, args.o)

if __name__ == '__main__':
    main()
