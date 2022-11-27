from re import compile
from os.path import join

ALPHANUMERIC = compile(r'[\w\d]')
STATEMENTS = ('if', 'else', 'elif', 'for', 'while', 'switch', 'try', 'catch', 'except', 'import', 'export', 'require', 'package')
STATEMENT = compile(r'\b(' + '|'.join(STATEMENTS) + r')\b')

def valid_line(line):
    if ALPHANUMERIC.search(line) and not STATEMENT.search(line):
        return True
    return False

def delete_lines(root, files):
    for file in sorted(files):
        print(file)
        file_path = join(root, file)
        with open(file_path, 'r') as code:
            code = code.read().split('\n')
        for i in range(len(code)):
            if valid_line(code[i]):
                mutant = (line for pos, line in enumerate(code) if pos != i)
                with open(file_path, 'w') as out:
                    out.write('\n'.join(mutant))
                yield file, i
        with open(file_path, 'w') as out:
            out.write('\n'.join(code))
