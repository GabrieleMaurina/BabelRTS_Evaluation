from babelrts.languages.javascript import Javascript

class Typescript(Javascript):
    def get_extensions_patterns_actions(self):
        extensions_patterns_actions = super().get_extensions_patterns_actions()
        for extension_pattern_action in extensions_patterns_actions:
            extension_pattern_action.extension = 'ts'
        return extensions_patterns_actions
