from utils.revisions import add_shas
from utils.folder_manager import get_repo, dump


TENSORFLOW_GIT = 'https://github.com/tensorflow/tensorflow.git'

TENSORFLOW_META = 'tensorflow_meta'


def main():
    tensorflow = get_repo(TENSORFLOW_GIT)
    add_shas(tensorflow, ('java',))

    print(tensorflow)
    dump(tensorflow, TENSORFLOW_META)


if __name__ == '__main__':
    main()
