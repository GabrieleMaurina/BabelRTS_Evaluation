from subprocess import run

def rc(cmd, cwd, timeout=None):
    return run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=timeout)
