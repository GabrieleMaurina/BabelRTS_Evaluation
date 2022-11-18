from utils.language import Language
from re import compile

FAILURES = compile(r'(\d+) failed')

class Python(Language):
    def test(self, tests=None):
        if tests:
            tests = " ".join(tests)
        else:
            tests = self.test_folder
        output = self.rc(f'python3.9 -m pytest {tests}')
        return search_failures(output, FAILURES)
