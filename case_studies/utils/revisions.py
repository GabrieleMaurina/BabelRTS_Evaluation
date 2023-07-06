from utils.run_cmd import rc
N_COMMITS = 20
CHANGED_FILES = 3

CPP_FILE_EXTENSIONS = ('c', 'h', 'cpp', 'hpp', 'cc')


def check_extension(name, extensions):
    if name:
        for ext in extensions:
            if name.endswith('.' + ext):
                return True
    return False


def n_changed(h1, h2, extensions, path):
    return sum(1 for name in rc(f'git --no-pager diff --name-only {h1} {h2}', path).stdout.split('\n') if check_extension(name, extensions))


def find_starting_commit(hashcodes, extensions, path):
    for i in range(len(hashcodes) - 1):
        if n_changed(hashcodes[i], hashcodes[i + 1], extensions, path) > 0:
            return i
    return 0


def get_commits(revs, changed_files, extensions, starting_commit_extensions, path):
    hashcodes = tuple(hash for hash in rc(
        'git --no-pager log --first-parent --pretty=tformat:"%H"', path).stdout.split('\n') if hash)
    if starting_commit_extensions:
        commit = find_starting_commit(
            hashcodes, starting_commit_extensions, path)
    else:
        commit = 0
    commits = [hashcodes[commit]]
    commit += 1
    for _ in range(revs):
        while n_changed(hashcodes[commit], commits[-1], extensions, path) < changed_files:
            commit += 1
        commits.append(hashcodes[commit])
    return list(reversed(commits))


def add_shas(repo, starting_commit_extensions=None):
    repo.shas = get_commits(N_COMMITS, CHANGED_FILES,
                            CPP_FILE_EXTENSIONS, starting_commit_extensions, repo.path)
