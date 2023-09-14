from sys import argv

from utils.run_cmd import rc
from utils.folder_manager import get_repo
import utils.subjects as subjects

CPP_FILE_EXTENSIONS = ('c', 'h', 'cpp', 'hpp', 'cc')

def count(path, h1, h2):
    git_command = f'git --no-pager diff --name-only {h1} {h2}'
    lines = rc(git_command, path).stdout.split('\n')
    java = 0
    python = 0
    cpp = 0
    for file in lines:
        if file.endswith('.java'):
            java += 1
        elif file.endswith('.py'):
            python += 1
        elif file.rsplit('.', 1)[-1] in CPP_FILE_EXTENSIONS:
            cpp += 1
    return java, python, cpp


def save_csv(subject, hashcodes, counts):
    with open(subjects.CHANGES[subject], 'w') as out:
        out.write(f'hashcode,{subject.JAVA},{subject.PYTHON},{subject.CPP}\n')
        for hashcode, count in zip(hashcodes, counts):
            out.write(f'{hashcode},{count[0]},{count[1]},{count[2]}\n')


def main(subject):
    repo = get_repo(subjects.GIT[subject])

    git_command = 'git --no-pager log --first-parent --pretty=tformat:"%H"'
    lines = reversed(rc(git_command, repo.path).stdout.split('\n'))
    hashcodes = tuple(hash for hash in lines if hash)

    counts = []
    for i in range(len(hashcodes) - 1):
        counts.append(count(repo.path, hashcodes[i], hashcodes[i + 1]))
        print(i, counts[-1])

    save_csv(subject, hashcodes[1:], counts)


if __name__ == '__main__':
    subject = argv[1]
    main(subject)
