import sys
from lib2to3.main import main as main_2to3
from lib2to3.refactor import RefactoringTool, get_fixers_from_package
from pathlib import Path


def main_pathlad(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = ['-f', 'paths_nested', '-f', 'paths'] + argv + ['-w', '-n', '--no-diffs']
    print('Pathlad: run lib2to3 with ', args)
    sys.path.insert(0, Path(__file__).parent.absolute())
    main_2to3('pathlad.custom_fixers', args=args)

    # TODO: post-hoc remove unused imports
    # try:
    #     from autoflake import main as main_autoflake
    #     sys.argv = ['--in-place','--imports=os,glob,pathlib','-r', argv]
    #     main_autoflake()
    # except ImportError:
    #     pass


def pathlab_string(input):
    sys.path.insert(0, Path(__file__).parent.absolute())
    refactoring_tool = RefactoringTool(fixer_names=get_fixers_from_package('pathlad.custom_fixers'))
    result = input
    result = str(refactoring_tool.refactor_string(result + '\n', 'paths'))[:-1]
    result = str(refactoring_tool.refactor_string(result + '\n', 'paths_nested'))[:-1]
    return result


if __name__ == "__main__":
    main_pathlad(argv=sys.argv)
