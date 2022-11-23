from utils.language import Language
from re import compile
from os.path import join

FAILURES = compile(r'Tests run: \d+, Failures: (\d+), Errors: (\d+), Skipped: \d+\n')
RAT_CONF = compile(r'<artifactId>apache-rat-plugin<\/artifactId>[\s\S]*?<configuration>')
RAT_SKIP = '<skip>true</skip>'
POM = 'pom.xml'

class Java(Language):
    def test(self, tests=None):
        dtest = ''
        if tests:
            classes = (file.split('/java/',1)[1].replace('/','.') for file in tests)
            tests = f'-Dtest={",".join(classes)}'
        else:
            tests = ''
        output = self.run(f'mvn clean test {tests}')
        return self.search_failures(output, FAILURES)

    def init_repo(self):
        self.insert_into_pom(RAT_SKIP, RAT_CONF)

    def insert_string(self, s1, s2, pos):
        return s1[:pos] + s2 + s1[pos:]

    def insert_into_pom(self, s, re):
        with open(join(self.project_folder, POM), 'r') as pom:
            pom = pom.read()
        res = re.search(pom)
        if res:
            pos = res.span()[1]
            with open(join(self.project_folder, POM), 'w') as out:
                out.write(self.insert_string(pom, s, pos))
