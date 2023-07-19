from os.path import join

from utils.run_cmd import rc
from utils.folder_manager import get_repo


TENSORFLOW_GIT = 'https://github.com/tensorflow/tensorflow.git'

RESULTS = 'results'
TENSORFLOW_CHANGES = join(RESULTS, 'tensorflow_changes.csv')

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


def save_csv(hashcodes, counts):
    with open(TENSORFLOW_CHANGES, 'w') as out:
        out.write('hashcode,java,python,cpp\n')
        for hashcode, count in zip(hashcodes, counts):
            out.write(f'{hashcode},{count[0]},{count[1]},{count[2]}\n')


def main():
    tensorflow = get_repo(TENSORFLOW_GIT)

    git_command = 'git --no-pager log --first-parent --pretty=tformat:"%H"'
    lines = reversed(rc(git_command, tensorflow.path).stdout.split('\n'))
    hashcodes = tuple(hash for hash in lines if hash)

    counts = []
    for i in range(len(hashcodes) - 1):
        counts.append(count(tensorflow.path, hashcodes[i], hashcodes[i + 1]))
        print(i, counts[-1])

    save_csv(hashcodes[1:], counts)


if __name__ == '__main__':
    main()
