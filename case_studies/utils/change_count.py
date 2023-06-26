
from collections import deque
import os

def change_count(babelRTS):
    count = 0

    test_files = babelRTS.get_change_discoverer().get_test_files()
    dependency_graph = babelRTS.get_dependency_extractor().get_dependency_graph()
    changed_files = babelRTS.get_change_discoverer().get_changed_files()

    for test_file in test_files:
        start_ext = os.path.splitext(test_file)
        visited_files = set()
        queue = deque(dependency_graph[test_file])
        while queue:
            for file in queue:
                ext = os.path.splitext(file)
                if file in visited_files:
                    continue
                visited_files.add(file)
                if start_ext[1].lower() != ext[1].lower() and file in changed_files:
                    count+= 1
                    break
                if file in dependency_graph:
                    queue.extend(dependency_graph[file])

    return count
                


