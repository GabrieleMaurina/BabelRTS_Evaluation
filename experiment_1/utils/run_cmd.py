from time import time
from subprocess import run

def rc(cmd):
    t = time()
    try:
        res = run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    except Exception as e:
        return None, '', str(e), time()-t
    else:
        returncode = res.returncode
        stdout = res.stdout if not res.stdout.endswith('\n') else res.stdout[:-1]
        stderr = res.stderr if not res.stderr.endswith('\n') else res.stderr[:-1]
        return returncode, stdout, stderr, time()-t
