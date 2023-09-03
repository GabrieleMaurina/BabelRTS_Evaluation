from collections import deque
import os

def experiment_function(babelRTS):
    count0 = 0
    count1 = 0
    count2 = 0

    test_files0 = babelRTS.get_change_discoverer().get_test_files()
    dependency_graph0 = babelRTS.get_dependency_extractor().get_dependency_graph()

    for test_file in test_files0:
        ext = test_file.rsplit('.',1)[-1]
        if test_file in dependency_graph0:
            queue = deque(dependency_graph0[test_file])
            visited = set()
            while queue:
                file = queue.pop()
                if file in visited:
                    continue
                visited.add(file)
                if ext != file.rsplit('.',1)[-1]:
                    count0 += 1
                    break
                if file in dependency_graph0:
                    queue.extend(dependency_graph0[file])

    test_files1 = babelRTS.get_change_discoverer().get_test_files()
    dependency_graph1 = babelRTS.get_dependency_extractor().get_dependency_graph()
    changed_files1 = babelRTS.get_change_discoverer().get_changed_files()

    for test_file in test_files1:
        start_ext = os.path.splitext(test_file)
        visited_files = set()
        queue = deque(dependency_graph1[test_file])
        while queue:
            for file in queue:
                ext = os.path.splitext(file)
                if file in visited_files:
                    continue
                visited_files.add(file)
                if start_ext[1].lower() != ext[1].lower() and file in changed_files1:
                    count1+= 1
                    break
                if file in dependency_graph1:
                    queue.extend(dependency_graph1[file])
                    
    test_files2 = babelRTS.get_change_discoverer().get_test_files()
    dependency_graph2 = babelRTS.get_dependency_extractor().get_dependency_graph()
    changed_files2 = babelRTS.get_change_discoverer().get_changed_files()

    for test_file in test_files2:
        start_ext = os.path.splitext(test_file)
        visited_files = set()
        queue = deque(dependency_graph1[test_file])
        while queue:
            for file in queue:
                ext = os.path.splitext(file)
                if file in visited_files:
                    continue
                visited_files.add(file)
                if start_ext[1].lower() != ext[1].lower() and file in changed_files2:
                    count2+= 1
                    break
                if start_ext[1].lower() == ext[1].lower() and file in changed_files2:
                    count2 = 0
                    return count0, count1, count2
                if file in dependency_graph2:
                    queue.extend(dependency_graph2[file])

    return count0, count1, count2