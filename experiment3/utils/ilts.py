from collections import deque

def count_ilts(babelRTS):
    ilts = 0
    test_files = babelRTS.get_change_discoverer().get_test_files()
    dependency_graph = babelRTS.get_dependency_extractor().get_dependency_graph()
    #changed_files = babelRTS.get_change_discoverer().get_changed_files()
    for test_file in test_files:
        ext = test_file.rsplit('.',1)[-1]
        if test_file in dependency_graph:
            queue = deque(dependency_graph[test_file])
            visited = set()
            while queue:
                file = queue.pop()
                if file in visited:
                    continue
                visited.add(file)
                if ext != file.rsplit('.',1)[-1]:
                    ilts += 1
                    break
                if file in dependency_graph:
                    queue.extend(dependency_graph[file])
    return ilts
