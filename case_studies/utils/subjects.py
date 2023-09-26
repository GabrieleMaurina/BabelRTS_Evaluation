from os.path import join

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
