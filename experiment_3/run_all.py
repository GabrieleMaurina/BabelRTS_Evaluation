import evaluate
import sys
import utils.subjects as subjects

def main():
    subject = sys.argv[1]
    history = int(sys.argv[2]) if len(sys.argv) > 2 else None
    for run in subjects.RUNS[subject]:
        print('running', run)
        evaluate.main(subject, run, history)


if __name__ == '__main__':
    main()
