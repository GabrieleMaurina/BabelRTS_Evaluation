from sys import argv

from utils.revisions import add_shas
from utils.folder_manager import get_repo, dump
import utils.subjects as subjects


def main(subject, k, delta, start):
    repo = get_repo(subjects.GIT[subject])
    add_shas(repo, subjects.CHANGES[subject], k, delta, start)

    print(repo)
    dump(repo, subjects.META[subject])


if __name__ == '__main__':
    subject = argv[1]
    k = int(argv[2])
    delta = int(argv[3])
    start = int(argv[4])
    main(subject, k, delta, start)
