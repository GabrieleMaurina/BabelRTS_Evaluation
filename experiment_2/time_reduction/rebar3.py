import os.path
import re
import subprocess
import sut


TIME_RE = re.compile(r'\[done in (.+) s\]\n')


class Rebar3(sut.SUT):

    @property
    def language(self):
        return 'erlang'

    def run_all_tests(self):
        result = subprocess.run(['rebar3', 'eunit'],
                                cwd=self.path, capture_output=True, text=True)
        return self._read_result(result)

    def run_tests(self, tests):
        if not tests:
            return 0.0
        tests = [os.path.basename(test).rsplit('.', 1)[0] for test in tests]
        tests_string = ','.join(tests)
        result = subprocess.run(['rebar3', 'eunit', f'--module={tests_string}'],
                                cwd=self.path, capture_output=True, text=True)
        return self._read_result(result)

    def _read_result(self, result):
        time = 0.0
        value = None
        for value in TIME_RE.findall(result.stdout):
            time += float(value)
        if value is None:
            return None
        return time
