from babelrts.languages.language import Language, ExtensionPatternAction
from re import compile as cmp_re
from glob import glob
from os.path import isfile, join
from itertools import chain

REQUIRE = cmp_re(r'require\s*\(\s*[\'"](.*)[\'"]\s*\)')
IMPORT = cmp_re(r'import\s[\s\S]+?\sfrom\s+[\'"](.*?)[\'"]')
EXPORT = cmp_re(r'export\s[\s\S]+?\sfrom\s+[\'"](.*?)[\'"]')

PATTERNS = (REQUIRE, IMPORT, EXPORT)

class Javascript(Language):
    def get_extensions_patterns_actions(self):
        return tuple(ExtensionPatternAction('js', pattern, self.import) for pattern in PATTERNS)

    def find_imports(self, match, file_path, folder_path, project_path, content):
        if match.endswith('.js') or match.endswith('.ts'):
            return {join(folder_path, match)}
        else:
            try:
                deps = set()
                for file in chain(glob(join(folder_path, match) + '*'), glob(join(folder_path, match, '*'))):
                    if isfile(join(project_folder, file)) and (file.endswith('.js') or file.endswith('.ts')):
                        deps.add(file)
                return deps
            except Exception:
                pass
