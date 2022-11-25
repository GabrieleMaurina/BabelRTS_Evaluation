from abc import ABC, abstractmethod
from utils.run_cmd import rc
from subprocess import TimeoutExpired

class Language:

    def __init__(self):
        self.set_project_folder('')
        self.set_test_folder('')

    def set_project_folder(self, project_folder):
        self.project_folder = project_folder

    def set_test_folder(self, test_folder):
        self.test_folder = test_folder

    def run(self, cmd):
        try:
            res = rc(cmd, cwd=self.project_folder, timeout=180)
            return res.stdout + '\n' + res.stderr
        except TimeoutExpired:
            return ''

    @abstractmethod
    def test(self, tests=None):
        pass

    def search_failures(self, text, re, missing_ok=True):
        match = re.search(text)
        if match:
            return sum(int(group) for group in match.groups())
        elif missing_ok:
            return 0
        else:
            return None

    def init_repo(self):
        pass
