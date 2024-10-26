from babelrts.components.dependencies.language import Language
from babelrts.components.dependencies.extension_pattern_action import ExtensionPatternAction

from re import compile as cmp_re

WHOLE_PATTERN = cmp_re(r'^[\s\S]*$')

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
        return (ExtensionPatternAction('py', WHOLE_PATTERN, self.init_native_action),)

    @staticmethod
    def get_language():
        return 'tensorflow'

    def init_native_action(self, match, file_path, folder_path, content):
        file_name = file_path.rsplit('/', 1)[-1]
        if file_name == '__init__.py':
            all_files = self.get_dependency_extractor().get_babelrts().get_change_discoverer().get_all_files()
            native_deps = tuple(file for file in all_files if file.startswith(folder_path) and not file.endswith('.py'))
            if native_deps:
                for _ in native_deps:
                    inc_count()
                return native_deps
