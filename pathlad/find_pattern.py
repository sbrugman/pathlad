import sys
from lib2to3.main import main
from lib2to3.refactor import RefactoringTool, get_fixers_from_package
from pathlib import Path

# https://stackoverflow.com/questions/24508357/how-to-launch-own-2to3-fixer

# Run using:
# ```python find_pattern.py -f paths cases/paths.py```

# To write to results dir:
# ```python find_pattern.py -f paths cases/paths.py -w -n -o results/```

# To overwrite
# # ```python find_pattern.py -f paths example.py -w```
def mainx(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = ['-f', 'paths'] + argv + ['-w', '-n', '--no-diffs']
    print('Pathlad: run lib2to3 with ', args)
    sys.path.insert(0, Path(__file__).parent.absolute())
    sys.exit(main('pathlad.custom_fixers', args=args))


def fix_str(input):
    sys.path.insert(0, Path(__file__).parent.absolute())
    refactoring_tool = RefactoringTool(fixer_names=get_fixers_from_package('pathlad.custom_fixers'))
    return str(refactoring_tool.refactor_string(input + '\n', 'paths'))[:-1]


if __name__ == "__main__":
    mainx(argv=sys.argv)
