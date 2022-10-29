from babelrts.languages.language import Language, ExtensionPatternAction
from re import compile as cmp_re
from glob import glob
from os.path import isdir, isfile, join

IMPORT = cmp_re(r'([^\S\r\n]*from[^\S\r\n]+(\S+)[^\S\r\n]+)?import[^\S\r\n](\S+)')

class Python(Language):
    def get_extensions_patterns_actions(self):
        return ExtensionPatternAction('py', IMPORT, self.import)

    def import(self, match, file_path, folder_path, project_folder, content):
        name = match[1] if match[1] else match[2]
        path = join(project_folder, name.replace('.', '/'))
        if isfile(file := path + '.py'):
            return {file}
        elif isdir(path):
            return set(glob(join(path, '*.py')))
