from collections import deque
from simpleobject import simpleobject as so
import utils.subjects as subjects


LANGUAGES = ('python', 'java', 'cpp')


def get_language(ext):
    if ext == 'py':
        return subjects.PYTHON
    elif ext == 'java':
        return subjects.JAVA
    return subjects.CPP


def different_language(ext1, ext2):
    return get_language(ext1) != get_language(ext2)


def count_tests(babelRTS):
    tests = so()
    for language in LANGUAGES:
        tests[language] = count_tests_language(babelRTS, language)
    tests.all = so(ilt=0, iltc=0, iltco=0)
    for language in LANGUAGES:
        tests.all.ilt += tests[language].ilts
        tests.all.iltc += tests[language].iltcs
        tests.all.iltco += tests[language].iltcos
    return tests


def count_tests_language(babelRTS, language):
    return so(ilts=0, iltcs=0, iltcos=0)

    ilt = set()
    iltc = set()
    iltcno = set()

    test_files = babelRTS.get_change_discoverer().get_test_files()
    changed_files = babelRTS.get_change_discoverer().get_changed_files()
    dependency_graph = babelRTS.get_dependency_extractor().get_dependency_graph()
    for test_file in test_files:
        ext = test_file.rsplit('.', 1)[-1]
        if language != get_language(ext):
            continue
        if test_file in changed_files:
            iltcno.add(test_file)
        if test_file in dependency_graph:
            queue = deque(dependency_graph[test_file])
            visited = set((test_file,))
            while queue:
                file = queue.pop()
                if file in visited:
                    continue
                visited.add(file)
                if different_language(ext, file.rsplit('.', 1)[-1]):
                    ilt.add(test_file)
                    if file in changed_files:
                        iltc.add(test_file)
                elif file in changed_files:
                    iltcno.add(test_file)
                if file in dependency_graph:
                    queue.extend(dependency_graph[file])

    iltco = iltc - iltcno
    return so(ilts=len(ilt), iltcs=len(iltc), iltcos=len(iltco))
