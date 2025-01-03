import subprocess
import time
import sut


class Rake(sut.SUT):

    @property
    def language(self):
        return 'ruby'
    
    def build(self):
        pass
        #subprocess.run(['bundle', 'install'], cwd=self.path, capture_output=True)

    def run_all_tests(self):
        start = time.time()
        subprocess.run(['bundle', 'exec', 'rake', 'test'], cwd=self.path, capture_output=True)
        return time.time() - start

    def run_tests(self, tests):
        if not tests:
            return 0.0
        tests = [f'TEST={test}' for test in tests]
        start = time.time()
        subprocess.run(['bundle', 'exec', 'rake', 'test'] + tests, cwd=self.path, capture_output=True)
        return time.time() - start
