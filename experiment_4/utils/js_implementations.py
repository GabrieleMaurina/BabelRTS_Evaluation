from babelrts.components.dependencies.languages import javascript
from babelrts.components.dependencies.extension_pattern_action import ExtensionPatternAction


import re
from os.path import join
from itertools import chain


BOWER_IMPORT = re.compile(r"helpers\.command\s*\(\s*'(.+?)'")


class Bower(javascript.Javascript):
    def get_extensions_patterns_actions(self):
        return super().get_extensions_patterns_actions() + (ExtensionPatternAction('js', BOWER_IMPORT, self.import_command_action), )

    def import_command_action(self, match, file_path, folder_path, content):
        return 'lib/commands/' + match + '.js'


ESLINT_RESOLVE = re.compile(r"resolve\s*\(\s*`\${__dirname}\/(.+?)`\)")


class Eslint(javascript.Javascript):
    def get_extensions_patterns_actions(self):
        return super().get_extensions_patterns_actions() + (ExtensionPatternAction('js', ESLINT_RESOLVE, self.import_action), )


KARMA_LOAD_FILE = re.compile(r"loadFile\s*\(.*?'\/(.+?)'")
KARMA_PROXYQUIRE = re.compile(r"proxyquire\s*\(\s*'(.*?)'")


class Karma(javascript.Javascript):
    def get_extensions_patterns_actions(self):
        return super().get_extensions_patterns_actions() + (ExtensionPatternAction('js', KARMA_LOAD_FILE, self.import_action), ExtensionPatternAction('js', KARMA_PROXYQUIRE, self.import_action))


PENCILBLUE_IMPORT = re.compile(r"require\s*\(.+?'\/(.+?)'")


class Pencilblue(javascript.Javascript):
    def get_extensions_patterns_actions(self):
        return super().get_extensions_patterns_actions() + (ExtensionPatternAction('js', PENCILBLUE_IMPORT, self.abs_import_action), )

    def abs_import_action(self, match, file_path, folder_path, content):
        if match.endswith('.js') or match.endswith('.ts'):
            if self.is_file(match):
                return match
        else:
            deps = set()
            for file in chain(self.expand(match + '*'), self.expand(join(match, '*'))):
                if self.is_file(file) and (file.endswith('.js') or file.endswith('.ts')):
                    deps.add(file)
            return deps


LANGUAGE_IMPLEMENTATIONS = {
    'Bower': [Bower],
    'Eslint': [Eslint],
    'Karma': [Karma],
    'Pencilblue': [Pencilblue],
}
