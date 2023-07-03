from utils.revisions import add_shas
from utils.folder_manager import get_repo, dump


TENSORFLOW_GIT = 'https://github.com/tensorflow/tensorflow.git'


def main():
    tensorflow = get_repo(TENSORFLOW_GIT)
    add_shas(tensorflow, ('java'))

    print(tensorflow.shas)
    dump('tensorflow_revisions', tensorflow)


if __name__ == '__main__':
    main()
