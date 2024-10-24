from utils.language import Language
from re import compile

FAILURES = compile(r'(\d+) failed')


class Python(Language):
    def test(self, tests=None):
        if tests:
            tests = ' '.join(tests)
        else:
            tests = self.test_folder
        output = self.run(f'python3.9 -m pytest {tests}')
        if 'error during collection' in output:
            return None
        return self.search_failures(output, FAILURES)
