from utils.run_cmd import rc

N_COMMITS = 1 #20
CHANGED_FILES = 3

CPP_FILE_EXTENSIONS = ('c', 'h', 'cpp', 'hpp', 'cc')

def check_extension(name):
    if name:
        for ext in CPP_FILE_EXTENSIONS:
            if name.endswith('.' + ext):
                return True
    return False

def n_changed(h1, h2, extensions, path):
    return sum(1 for name in rc(f'git --no-pager diff --name-only {h1} {h2}', path).stdout.split('\n') if check_extension(name, extensions))

def get_commits(revs, changed_files, extensions, path):
    hashcodes = tuple(hash for hash in rc('git --no-pager log --first-parent --pretty=tformat:"%H"', path).stdout.split('\n') if hash)
    commits = [hashcodes[0]]
    p = 1
    for i in range(revs):
        while n_changed(hashcodes[p], commits[-1], extensions, path) < changed_files:
            p += 1
        commits.append(hashcodes[p])
    return list(reversed(commits))

def add_shas(repo):
    repo.shas = get_commits(N_COMMITS, CHANGED_FILES, repo.path)
