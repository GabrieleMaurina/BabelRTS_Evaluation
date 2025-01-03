import abc
import os.path


DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(DIR, os.pardir))
REPOS_DIR = os.path.join(ROOT_DIR, 'repos')


class SUT(abc.ABC):

    @property
    def name(self):
        return self.__class__.__name__.lower()

    @property
    def path(self):
        return os.path.join(REPOS_DIR, self.name)

    @property
    @abc.abstractmethod
    def language(self):
        pass

    def build(self):
        pass

    @abc.abstractmethod
    def run_all_tests(self):
        pass

    @abc.abstractmethod
    def run_tests(self, tests):
        pass
