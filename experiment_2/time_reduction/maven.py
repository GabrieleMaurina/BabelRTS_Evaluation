import os.path
import subprocess
import time
import sut


class Maven(sut.SUT):

    @property
    def language(self):
        return 'java'
    
    def build(self):
        subprocess.run(['mvn', 'clean', 'install'], cwd=self.path, capture_output=True)

    def run_all_tests(self):
        start = time.time()
        subprocess.run(['mvn', 'test'], cwd=self.path, capture_output=True)
        return time.time() - start

    def run_tests(self, tests):
        if not tests:
            return 0.0
        tests = [os.path.basename(test).rsplit('.', 1)[0] for test in tests]
        tests_string = '-Dtest=' + ','.join(tests)
        start = time.time()
        subprocess.run(['mvn', tests_string, 'test'], cwd=self.path, capture_output=True)
        return time.time() - start
