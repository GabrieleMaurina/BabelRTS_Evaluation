from abc import ABC, abstractmethod

class Language(ABC):
    @abstractmethod
    def get_extensions_patterns_actions(self):
        pass

class ExtensionPatternAction:
    def __init__(self, extension, pattern, action):
        self.extension = extension
        self.pattern = pattern
        self.action = action
