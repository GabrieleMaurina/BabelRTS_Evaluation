from os.path import join
from utils.revisions import add_shas
from utils.folder_manager import get_repo, dump


TENSORFLOW_GIT = 'https://github.com/tensorflow/tensorflow.git'

TENSORFLOW_META = join('tensorflow_meta')


def main():
    tensorflow = get_repo(TENSORFLOW_GIT)
    add_shas(tensorflow, ('java'))

    print(tensorflow.shas)
    dump(TENSORFLOW_META, tensorflow)


if __name__ == '__main__':
    main()
