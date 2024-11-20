from babelrts.components.dependencies.languages import java
from babelrts.components.dependencies.extension_pattern_action import ExtensionPatternAction


import re


MOCKITO_LOAD_PLUGIN = re.compile(r'loadPlugin\(.+?"(.+?)"')


class Mockito(java.Java):
    def get_extensions_patterns_actions(self):
        return super().get_extensions_patterns_actions() + (ExtensionPatternAction('java', MOCKITO_LOAD_PLUGIN, self.used_class_action), )


JXPATH_PARSER_CLASSES = re.compile(
    r'parserClasses\.put\(\s*MODEL_J?DOM\s*,\s*"(\S+?)"\s*\)')

JXPATH_ALLOCATE_CONDITIONALLY = re.compile(
    r'allocateConditionally\(\s*"(\S+?)"')

JXPATH_FACTORIES = re.compile(
    r'(?:FACTORY_NAME_PROPERTY|DEFAULT_FACTORY_CLASS)\s*=\s*"(\S+?)"')


class JxPath(java.Java):
    def get_extensions_patterns_actions(self):
        return super().get_extensions_patterns_actions() + (
            ExtensionPatternAction(
                'java', JXPATH_PARSER_CLASSES, self.used_class_action),
            ExtensionPatternAction(
                'java', JXPATH_ALLOCATE_CONDITIONALLY, self.used_class_action),
            ExtensionPatternAction('java', JXPATH_FACTORIES, self.used_class_action))


LANGUAGE_IMPLEMENTATIONS = {
    'JxPath': [JxPath],
    'Mockito': [Mockito],
}
