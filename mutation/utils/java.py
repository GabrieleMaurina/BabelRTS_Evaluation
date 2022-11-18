from utils.language import Language
from re import compile

FAILURES = compile(r'Tests run: \d+, Failures: (\d+), Errors: \d+, Skipped: \d+\n')

class Java(Language):
    def test(self, tests=None):
        dtest = ''
        if tests:
            classes = (file.split('/java/',1)[1].replace('/','.') for file in tests)
            tests = f'-Dtest={",".join(classes)}'
        else:
            tests = ''
        output = self.rc(f'mvn clean test {tests}')
        return search_failures(output, FAILURES)
