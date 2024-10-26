from utils.language import Language
from re import compile

FAILURES = compile(r'Tests:\s+(\d+) failed')

class Javascript(Language):
    def test(self, tests=None):
        if tests:
            tests = ' '.join(tests)
        else:
            tests = self.test_folder
        output = self.run(f'jest {tests}')
        return self.search_failures(output, FAILURES)

    def init_repo(self):
        self.run('npm i --force')
