from utils.language import Language
from re import compile

FAILURES = compile(r'Tests:\s+(\d+) failed')

class Javascript(Language):
    def test(self, tests=None):
        if tests:
            tests = ' '.join(tests)
        else:
            tests = self.test_folder
        output.self.rc(f'jest {tests}')
        return search_failures(output, FAILURES)

    def init_repo(self):
        self.rc('npm i --force')
