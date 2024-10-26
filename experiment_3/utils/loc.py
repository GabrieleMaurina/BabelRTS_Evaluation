from utils.run_cmd import rc

def get_loc(root, files):
    if files:
        K = 100
        files = tuple(files)
        partition = (files[i:i+K] for i in range(0, len(files), K))
        def loc(paths):
            return int(rc(f'wc -l ' + ' '.join(paths), root).stdout.split('\n')[-2].rsplit(' ', 1)[0])
        return sum(loc(paths) for paths in partition)
    else:
        return 0
