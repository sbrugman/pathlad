# Pathlad
_Your friendly Python Path Converter_

Python 3.4 introduced [Pathlib](https://docs.python.org/3/library/pathlib.html), a clean object-oriented cross-platform way of handling paths. If the examples in the docs do not convince you yet, please read these blog posts by Trey Hunner:  [Why you should be using Pathlib](https://treyhunner.com/2018/12/why-you-should-be-using-pathlib/) and [No really, pathlib is great](https://treyhunner.com/2019/01/no-really-pathlib-is-great/).
Don't let your codebases be another one full with unnecessary path logic.

## What it does

1. Parses your Python code and automatically fix prehistoric file manipulations.

2. Helps you kickstart with refactoring you legacy code paths. Don't expect it to do all the work for you (yet). The best part: even if it makes a mistake, you know already where to look.

3. Profit.

## Example
Before:
```python
import os

os.path.isdir(os.path.join(__file__, "../test"))
```

After:

```python
from pathlib import Path

(Path(__file__) / ".." / "test").is_dir()
```

You can find more examples in the [examples](examples/input/) directory.

## Installation

Installation via pip:

`pip install pathlad`

## Usage

Command line interface:

`pathlad [dirname]`

## API Coverage

- [X] [Pathlib's equivalences](https://docs.python.org/3.8/library/pathlib.html#correspondence-to-tools-in-the-os-module)
- [X] `os.makedirs`
- [X] `os.path.normpath`
- [X] `os.path.realpath`
- [X] `open`
- [X] `os.path.getsize`
- [X] `os.listdir`
- [X] Nested calls
- [ ] `glob.glob`
- [ ] `Path.write_*`
- [ ] `from os import method`

## Advanced Usage options

**Warning:** pathlad is under active development, the API might change without notice.

pathlad is built on top of [2to3](https://docs.python.org/3/library/2to3.html) (just like [black](https://github.com/psf/black)). For now, the options are identical.

```bash
Usage: pathlad [options] file|dir ...

Options:
  -h, --help            show this help message and exit
  -j PROCESSES, --processes=PROCESSES
                        Run 2to3 concurrently
  -x NOFIX, --nofix=NOFIX
                        Prevent a transformation from being run
  -v, --verbose         More verbose logging
  --no-diffs            Don't show diffs of the refactoring
  -w, --write           Write back modified files
  -n, --nobackups       Don't write backups for modified files
  -o OUTPUT_DIR, --output-dir=OUTPUT_DIR
                        Put output files in this directory instead of
                        overwriting the input files.  Requires -n.
  -W, --write-unchanged-files
                        Also write files even if no changes were required
                        (useful with --output-dir); implies -w.
  --add-suffix=ADD_SUFFIX
                        Append this string to all output filenames. Requires
                        -n if non-empty.  ex: --add-suffix='3' will generate
                        .py3 files.
```

## Tips

- `pathlad` doesn't care about formatting. For the best results, run [`isort`](https://github.com/timothycrosley/isort) and [`black`](https://github.com/psf/black/) afterwards.

- `pathlib` is generally slower than `os.path`, especially when creating lots of `Path` objects. In most cases however, such as dataset creation scripts and tests, this doesn't weigh up to the value of readable, maintainable code.

## Contributing

> However, being a programmer - I'm too lazy to spend 8 hours mindlessly performing a function, but not too lazy to spend 16 hours automating it. 

~ Timothy Crosley

Pull-requests are welcome.

Helpful contributions include:
- Extending API coverage for `os`, `glob`, `shutils`
- More robust fixing w.r.t. spacing, optional arguments etc. 
- A method validation only (for example, a `--check-only` flag)
- A pre-commit hook
- Typing of some kind
- Basically any feature you see in `black` or `isort` etc. 
- Remove unused `os`, `glob` imports (`flake8 --select F401`, `autoflake --in-place --imports=os,glob,pathlib`) 

## Resources

- http://python3porting.com/2to3.html
- http://python3porting.com/fixers.html
- https://lucumr.pocoo.org/2010/2/11/porting-to-python-3-a-guide/
- https://docs.python.org/3/library/pathlib.html#correspondence-to-tools-in-the-os-module
- https://github.com/python/cpython/tree/3.8/Lib/lib2to3/fixes
- https://stackoverflow.com/questions/24508357/how-to-launch-own-2to3-fixer
