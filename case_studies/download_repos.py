from sys import argv

from utils.revisions import add_shas
from utils.folder_manager import get_repo, dump
import utils.subjects as subjects


def main(subject, start_commit, commit_size):
    repo = get_repo(subjects.GIT[subject])
    add_shas(repo, start_commit, commit_size)

    print(repo)
    dump(repo, subjects.META[subject])


if __name__ == '__main__':
    subject = argv[1]
    start_commit = int(argv[2])
    commit_size = int(argv[3])
    main(subject, start_commit, commit_size)
