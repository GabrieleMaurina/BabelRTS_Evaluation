import babelrts
import utils.results


import time


def run_rts(project_folder, src_folder, test_folder, failing_tests, language, extension, sut, bug, results_csv, test_regexp=None, language_implementations=None):
    loc = utils.results.get_loc(project_folder, extension)
    rts = babelrts.BabelRTS(project_folder,
                            src_folder,
                            test_folder,
                            languages=language,
                            test_regexp=test_regexp,
                            language_implementations=language_implementations)
    tot_time = time.time()
    selected_tests = rts.rts()
    tot_time = time.time() - tot_time
    selected_tests = set(selected_tests)

    sources = rts.get_change_discoverer().get_source_files()
    tot_sources = len(sources)
    tests = rts.get_change_discoverer().get_test_files()
    tot_tests = len(tests)
    test_suite_reduction = 1.0 - len(selected_tests) / tot_tests

    failing_tests = set(failing_tests).intersection(tests)
    detected = failing_tests.issubset(selected_tests)
    utils.results.store_results(results_csv,
                                sut,
                                bug,
                                detected,
                                tot_time,
                                test_suite_reduction,
                                tot_sources,
                                tot_tests,
                                loc)
    # print(selected_tests)
    # print(rts.get_change_discoverer().get_changed_files())
    # print(failing_tests)
    # deps = rts.get_dependency_extractor().get_dependencies()
    # deps = {k: tuple(v) for k, v in deps.items()}
    # import json
    # with open('deps.json', 'w') as f:
    #     json.dump(deps, f, indent=4)
    return detected, tot_time, test_suite_reduction, tot_sources, tot_tests, loc
