from abc import ABC, abstractmethod
from utils.run_cmd import rc

class Language:

    def __init__(self):
        self.set_project_folder('')
        self.set_test_folder('')

    def set_project_folder(self, project_folder):
        self.project_folder = project_folder
        self.init_repo()

    def set_test_folder(self, test_folder):
        self.test_folder = test_folder

    def run(self, cmd):
        return rc(cmd, cwd=self.project_folder).stdout

    @abstractmethod
    def test(self, tests=None):
        pass

    def search_failures(output, re):
        match = re.search(output)
        if match:
            return int(match[1])
        else:
            return None

    def init_repo(self):
        pass
