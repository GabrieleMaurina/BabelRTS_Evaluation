import os
import os.path
import re
import shutil
import subprocess
import time
import sut


TEST_RE = re.compile(r'\d+\/\d+\s+Test\s+#\d+:\s+(\S+?)\s+\.+\s+\w+\s+([\d.]+)\ssec')


class GoogleTest(sut.SUT):

    def __init__(self):
        self.last_test_times = None
        self.my_build = os.path.join(self.path, 'mybuild')

    @property
    def language(self):
        return 'c++'
    
    def build(self):
        if os.path.exists(self.my_build):
            shutil.rmtree(self.my_build)
        os.makedirs(self.my_build)
        subprocess.run(['cmake', '-Dgtest_build_tests=ON', '-Dgmock_build_tests=ON', '..'], cwd=self.my_build, capture_output=True, check=True)
        subprocess.run(['make'], cwd=self.my_build, capture_output=True, check=True)

    def run_all_tests(self):
        output = subprocess.run(['make', 'test'], cwd=self.my_build, capture_output=True, text=True, check=True).stdout
        self.last_test_times = {}
        total_time = 0.0
        for test_name, test_duration in TEST_RE.findall(output):
            test_duration = float(test_duration)
            self.last_test_times[test_name] = test_duration
            total_time += test_duration
        return total_time

    def run_tests(self, tests):
        if not tests:
            return 0.0
        total_time = 0.0
        for test in tests:
            name = os.path.basename(test).rsplit('.', 1)[0]
            if name in self.last_test_times:
                total_time += self.last_test_times[name]
        self.last_test_times = None
        return total_time
