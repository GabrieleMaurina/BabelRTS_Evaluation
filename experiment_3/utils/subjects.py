from os.path import join, relpath
from os import walk, sep
from re import compile as cmp_re

RESULTS = 'results'

JAVA = 'java'
PYTHON = 'python'
CPP = 'c++'
ALL = 'all'

TENSORFLOW = 'tensorflow'
OPENJDK = 'openjdk'

TENSORFLOW_GIT = 'https://github.com/tensorflow/tensorflow.git'
OPENJDK_GIT = 'https://github.com/openjdk/jdk.git'

GIT = {TENSORFLOW : TENSORFLOW_GIT, OPENJDK : OPENJDK_GIT}

TENSORFLOW_META = 'tensorflow_meta'
OPENJDK_META = 'openjdk_meta'

META = {TENSORFLOW : TENSORFLOW_META, OPENJDK : OPENJDK_META}

TENSORFLOW_CHANGES = join(RESULTS, 'tensorflow_changes.csv')
OPENJDK_CHANGES = join(RESULTS, 'openjdk_changes.csv')

CHANGES = {TENSORFLOW : TENSORFLOW_CHANGES, OPENJDK : OPENJDK_CHANGES}

TENSORFLOW_CONSECUTIVE_CHANGES = join(RESULTS, 'tensorflow_consecutive_changes.csv')
OPENJDK_CONSECUTIVE_CHANGES = join(RESULTS, 'openjdk_consecutive_changes.csv')

CONSECUTIVE_CHANGES = {TENSORFLOW : TENSORFLOW_CONSECUTIVE_CHANGES, OPENJDK : OPENJDK_CONSECUTIVE_CHANGES}

TENSORFLOW_BEST_WINDOW = 'tensorflow_best_window'
OPENJDK_BEST_WINDOW = 'openjdk_best_window'

BEST_WINDOW = {TENSORFLOW : TENSORFLOW_BEST_WINDOW, OPENJDK : OPENJDK_BEST_WINDOW}

TENSORFLOW_LANGUAGES = (JAVA, PYTHON, CPP)
OPENJDK_LANGUAGES = (JAVA, CPP)

LANGUAGES = {TENSORFLOW : TENSORFLOW_LANGUAGES, OPENJDK : OPENJDK_LANGUAGES}

TENSORFLOW_CHANGES_PLOT = join(RESULTS, 'tensorflow_changes.png')
OPENJDK_CHANGES_PLOT = join(RESULTS, 'openjdk_changes.png')

CHANGES_PLOT = {TENSORFLOW : TENSORFLOW_CHANGES_PLOT, OPENJDK : OPENJDK_CHANGES_PLOT}

TENSORFLOW_RUNS = {
    PYTHON: (PYTHON,),
    CPP: (CPP,),
    JAVA: (JAVA,),
    ALL: (PYTHON, CPP, JAVA, TENSORFLOW)
}

OPENJDK_RUNS = {
    JAVA: (JAVA,),
    CPP: (CPP,),
    ALL: (JAVA, CPP, OPENJDK)
}

RUNS = {TENSORFLOW : TENSORFLOW_RUNS, OPENJDK : OPENJDK_RUNS}

TENSORFLOW_SRC_FOLDERS = ['tensorflow/core',
                          'tensorflow/python',
                          'tensorflow/java/src/main/java',
                          'tensorflow/java/src/main/native']
TENSORFLOW_TEST_FOLDERS = ['tensorflow/python/kernel_tests',
                           'tensorflow/java/src/test/java']

def get_tensorflow_src_folders():
    return TENSORFLOW_SRC_FOLDERS

def get_tensorflow_test_folders():
    return TENSORFLOW_TEST_FOLDERS

def get_openjdk_folders(path, type):
    for root, dirs, _ in walk(path):
        if type in dirs:
            yield join(root, type)

OPENJDK_PATH = join('repos', 'jdk')

def get_openjdk_src_folders():
    main_source_folder = join(OPENJDK_PATH, 'src')

    java = get_openjdk_folders(main_source_folder, 'classes')
    native = get_openjdk_folders(main_source_folder, 'native')

    java_source_folders = tuple(relpath(source_folder, OPENJDK_PATH) for source_folder in java)
    native_source_folders = tuple(relpath(source_folder, OPENJDK_PATH) for source_folder in native)

    return java_source_folders + native_source_folders

PACKAGE_PATTERN = cmp_re(r'\bpackage\s+(\S+)\s*;')

def safe_read(file):
    try:
        with open(file, 'r') as content:
            return content.read()
    except Exception:
        encodings = ('utf8', 'unicode_escape', 'ascii', 'cp932')
        for encoding in encodings:
            try:
                with open(file, 'r', encoding=encoding) as content:
                    return content.read()
            except Exception:
                pass
    raise UnicodeError(f'Unable to read {file}')

def get_openjdk_test_folders():
    main_test_folder = join(OPENJDK_PATH, 'test')
    test_folders = {'test'}
    for root, _, files in walk(main_test_folder):
        for file in files:
            if file.endswith('.java'):
                path = join(root, file)
                content = safe_read(path)
                package = PACKAGE_PATTERN.search(content)
                if package:
                    package = package.group(1)
                    package_path = package.replace('.', sep)
                    if root.endswith(package_path):
                        folder = relpath(root[:-len(package_path)], OPENJDK_PATH)
                        test_folders.add(folder)
    return tuple(test_folders)

SRC_FOLDERS = {TENSORFLOW : get_tensorflow_src_folders, OPENJDK : get_openjdk_src_folders}
TEST_FOLDERS = {TENSORFLOW : get_tensorflow_test_folders, OPENJDK : get_openjdk_test_folders}

JSON = {subject: {run: {history: join(RESULTS, f'{subject}{"_history" if history else ""}_{run}.json') for history in (True, False)} for run in runs} for subject, runs in RUNS.items()}

AGGREGATED_CSV = {subject: {history: join(RESULTS, f'{subject}{"_history" if history else ""}.csv') for history in (True, False)} for subject in META}

STATS = {subject: {history: join(RESULTS, f'{subject}_stats{"_history" if history else ""}.txt') for history in (True, False)} for subject in META}

OUTPUT = {subject: {history: join(RESULTS, f'{subject}{"_history" if history else ""}.csv') for history in (True, False)} for subject in META}
