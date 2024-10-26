from os.path import join
from re import compile as recmp
from simpleobject import simpleobject as so
from utils.run_cmd import rc

MVN_TESTS = recmp(r'Running (\S+)\n')
RAT_CONF = recmp(r'<artifactId>apache-rat-plugin<\/artifactId>[\s\S]*?<configuration>')
RAT_SKIP = '<skip>true</skip>'
HYRTS = '<plugin><groupId>org.hyrts</groupId><artifactId>hyrts-maven-plugin</artifactId><version>1.0.1</version></plugin>'
EKSTAZI = '<plugin><groupId>org.ekstazi</groupId><artifactId>ekstazi-maven-plugin</artifactId><version>5.3.0</version><executions><execution><id>ekstazi</id><goals><goal>select</goal></goals></execution></executions></plugin>'
PLUGINS = recmp('<plugins>')
MISSING_PLUGINS = '<build><plugins></plugins></build>'
DEPENDENCIES = recmp('</dependencies>')
POM = 'pom.xml'

def insert_string(s1, s2, pos):
    return s1[:pos] + s2 + s1[pos:]

def insert_into_pom(s, re, missing=None, position=None):
    with open(POM, 'r') as pom:
        pom = pom.read()
    res = re.search(pom)
    if res:
        pos = res.span()[1]
        with open(POM, 'w') as out:
            out.write(insert_string(pom, s, pos))
    elif missing and position:
        pos = position.search(pom).span()[1]
        with open(POM, 'w') as out:
            out.write(insert_string(pom, missing, pos))
        insert_into_pom(s, re)


def build_java_project():
    insert_into_pom(HYRTS, PLUGINS, MISSING_PLUGINS, DEPENDENCIES)
    insert_into_pom(EKSTAZI, PLUGINS, MISSING_PLUGINS, DEPENDENCIES)
    insert_into_pom(RAT_SKIP, RAT_CONF)
    rc('mvn clean install -DskipTests -Drat.ignoreErrors=true')

def collect_java_tests(test_folder, res):
    selected_tests = tuple(join(test_folder, *name.split('.')) + '.java' for name in MVN_TESTS.findall(res[1]))
    duration = res[3]
    return so(tests=sorted(selected_tests), duration=duration)

def run_junit_tests(test_folder):
    res = rc(f'mvn clean test -Drat.ignoreErrors=true')
    return collect_java_tests(test_folder, res)

def run_hyrts_tests(test_folder, hash=None):
    res = rc(f'mvn clean hyrts:HyRTS -Drat.ignoreErrors=true')
    return collect_java_tests(test_folder, res)

def run_ekstazi_tests(test_folder, hash=None):
    res = rc(f'mvn clean ekstazi:ekstazi -Drat.ignoreErrors=true')
    return collect_java_tests(test_folder, res)

def run_babelrts_java_tests(selected_tests):
    selected_classes = (file.split('/java/',1)[1].replace('/','.') for file in selected_tests)
    rc(f'mvn test -Dtest={",".join(selected_classes)} -Drat.ignoreErrors=true')
