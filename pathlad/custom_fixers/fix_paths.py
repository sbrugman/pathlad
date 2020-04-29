import re
import symbol
from lib2to3.pgen2 import token
from lib2to3.pytree import Leaf
from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Attr, Call, Name, Number, Subscript, Node, syms, String, ArgList

# References:
# http://python3porting.com/2to3.html
# http://python3porting.com/fixers.html
# https://lucumr.pocoo.org/2010/2/11/porting-to-python-3-a-guide/
# https://docs.python.org/3/library/pathlib.html#correspondence-to-tools-in-the-os-module

Slash = Leaf(token.SLASH, "/", prefix=" ")


class FixPaths(BaseFix):
    BM_compatible = True
    PATTERN = """
              import_name<
                'import'
                 imp=any
              >
              |
              power< 
                module='os' 
                trailer< dot='.' method=('makedirs' | 'mkdir' | 'unlink' | 'remove' | 'rmdir' | 'rename' | 'replace' | 'stat' | 'chmod' | 'link' | 'listdir') >
                trailer< '(' obj=any ')'>
              >
              |
              power< 
                buildin='open' 
                trailer< '(' obj=any ')'>
              >
              |
              power< 
                module='os' 
                trailer< dot='.' method=('getcwd' | 'listdir') >
                trailer< '(' ')'>
              >
              |
              power< 
                module='os' 
                trailer< dot='.' submod='path' >
                trailer< '.' method=('isabs' | 'isdir' | 'isfile' | 'islink' | 'exists' | 'basename' | 'dirname' | 'expanduser' | 'join' | 'abspath' | 'realpath' | 'normpath' | 'same' | 'getsize') >
                trailer< '(' obj=any ')'>
              >
              """
    split_strings = False

    def _handle_import(self, node, results):
        y = node
        if len(node.children) >= 1 and node.children[1]:
            if isinstance(results['imp'], Leaf) and results['imp'].value in ['os', 'os.path']:
                y.append_child(String("\nfrom pathlib import Path"))

        return y

    def _handle_no_args(self, node, method_name):
        if method_name == "getcwd":
            method_name = "cwd"

        if method_name == "listdir":
            return Call(Name('list'), [Call(Name('Path(".").glob'), args=[String('"*"')])], prefix=node.prefix)

        return Call(Name('Path.{}'.format(method_name)), prefix=node.prefix)

    def _split_arguments(self, arglist):
        res = None
        for i, arg in enumerate(arglist.children):
            if arg.type == token.COMMA:
                res = i
                break

        remaining_args = []
        if res is not None:
            first_arg = [String(arg) for arg in arglist.children[:res]]

            if len(first_arg) >= 2:
                if first_arg[0].value == 'path' and first_arg[1].value == '=':
                    first_arg = first_arg[2:]

            for i, z in enumerate(arglist.children[res + 1:]):
                if i <= 1:
                    z.prefix = ""
                else:
                    z.prefix = " "
                remaining_args.append(String(z))
        else:
            arg = String(arglist)
            # Drop `path=`
            if isinstance(arg, Leaf) and len(arg.value.children) >= 3 and arg.value.children[0].value == 'path':
                arg.value.children = arg.value.children[2:]
            first_arg = [arg]

        return first_arg, remaining_args

    def transform(self, node: Node, results):
        if "imp" in results:
            return self._handle_import(node, results)
        else:
            if "buildin" in results:
                method_name = results["buildin"].value
                return self._handle_buildin(node, method_name)

            if isinstance(results['method'], Leaf):
                method_name = results["method"].value
            else:
                method_name = results["method"][0].value

            if "obj" not in results:
                # Prefix: Path.
                return self._handle_no_args(node, method_name)
            else:
                obj = results["obj"]
                argname = obj.clone()
                if "submod" in results:
                    if method_name == "join" and len(argname.children) >= 1:
                        first_arg, remaining_args = self._split_arguments(argname)

                        x = Call(Name("Path"), first_arg, prefix=node.prefix)

                        if len(remaining_args) > 0 and all(a.type in [token.COMMA, token.STRING] for a in remaining_args):
                            if str(remaining_args[0].value).startswith('*'):
                                x.append_child(Call(Name('joinpath', prefix=""), remaining_args, prefix="."))
                                return x
                            x.append_child(Slash)

                            for e in remaining_args:
                                if isinstance(e.value, Node):
                                    val = e.value
                                elif isinstance(e.value, Leaf):
                                    val = e.value.value
                                else:
                                    val = ""

                                if e.type == token.STRING and val != ",":
                                    # if self.split_strings and "/" in e.value:
                                    #     # TODO: get more robust e.value without quotes
                                    #     parts = re.split('(/|\\\\)', e.value[1:-1])
                                    #     for part in parts:
                                    #         if part in ["/", "\\"]:
                                    #             x.append_child(Slash)
                                    #         else:
                                    #             x.append_child(String('"{}"'.format(part), prefix=" "))
                                    # else:
                                    x.append_child(String(e, prefix=" "))
                                else:
                                    x.append_child(Slash)

                        return x
                    else:
                        first_arg, remaining_args = self._split_arguments(argname)

                        x = Call(Name("Path"), first_arg, prefix=node.prefix)

                        new_names = {
                            "isabs": "is_absolute",
                            "isdir": "is_dir",
                            "isfile": "is_file",
                            "islink": "is_symlink",
                            "abspath": "resolve",
                            "realpath": "resolve",
                            "normpath": "resolve",
                            "same": "samefile",
                        }
                        new_attribs = {
                            "basename": "name",
                            "dirname": "parent",
                            "getsize": "stat().st_size",
                        }
                        if method_name in new_names:
                            x.append_child(Call(Name(new_names[method_name], prefix=""), remaining_args, prefix="."))
                        elif method_name in new_attribs:
                            x.append_child(String(new_attribs[method_name], prefix="."))
                        else:
                            x.append_child(Call(Name(method_name, prefix=""), remaining_args, prefix="."))
                        return x
                else:
                    arglist = argname
                    first_arg, remaining_args = self._split_arguments(arglist)

                    x = Call(Name("Path"), first_arg, prefix=node.prefix)
                    if method_name == "remove":
                        method_name = "unlink"

                    if method_name == "listdir":
                        x.append_child(String('glob("*")', prefix="."))
                        x.prefix = ""
                        return Call(Name('list'), [x], prefix=node.prefix)
                    elif method_name == 'makedirs':
                        if len(remaining_args) > 0:
                            children = [Leaf(12, ','), Leaf(1, 'parents', prefix=' '), Leaf(22, '='), Leaf(3, 'True')]

                            remaining_args += [Node(type=260, children=children)]
                        else:
                            remaining_args = [Leaf(1, 'parents', prefix=''), Leaf(22, '='), Leaf(3, 'True')]

                        x.append_child(Call(Name("mkdir"), remaining_args, prefix="."))
                    else:
                        x.append_child(Call(Name(method_name), remaining_args, prefix="."))
                    return x

    def _handle_buildin(self, node, method_name):
        if method_name == "open":
            arglist = node.children[1].children[1]
            first_arg, remaining_args = self._split_arguments(arglist)

            x = Call(Name("Path"), first_arg, prefix=node.prefix)
            x.append_child(Call(Name("open"), remaining_args, prefix="."))
            return x
        else:
            raise ValueError("Method not found")
