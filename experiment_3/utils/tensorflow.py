from babelrts.components.dependencies.language import Language
from babelrts.components.dependencies.extension_pattern_action import ExtensionPatternAction

from re import compile as cmp_re
from os.path import basename

WHOLE_PATTERN = cmp_re(r'^[\s\S]*$')
LOAD_LIBRARY_PATTERN = cmp_re(r'System.loadLibrary\("(.+?)"\)')

count = 0


def inc_count():
    global count
    count += 1


def get_count():
    global count
    return count


def reset_count():
    global count
    count = 0


class Tensorflow(Language):
    def get_extensions_patterns_actions(self):
        return (ExtensionPatternAction('py', WHOLE_PATTERN, self.init_native_action),
                ExtensionPatternAction('java', LOAD_LIBRARY_PATTERN, self.load_library_action))

    @staticmethod
    def get_language():
        return 'tensorflow'

    def init_native_action(self, match, file_path, folder_path, content):
        file_name = basename(file_path)
        if file_name == '__init__.py':
            all_files = self.get_dependency_extractor(
            ).get_babelrts().get_change_discoverer().get_all_files()
            native_deps = tuple(file for file in all_files if file.startswith(
                folder_path) and not file.endswith('.py'))
            if native_deps:
                for _ in native_deps:
                    inc_count()
                return native_deps

    def load_library_action(self, match, file_path, folder_path, content):
        all_files = self.get_dependency_extractor(
        ).get_babelrts().get_change_discoverer().get_all_files()
        folder = folder_path.rsplit('java', 1)[0] + 'native'
        native_deps = tuple(
            file for file in all_files if file.startswith(folder))
        if native_deps:
            for _ in native_deps:
                inc_count()
            return native_deps

