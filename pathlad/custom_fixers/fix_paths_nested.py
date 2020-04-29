from lib2to3.fixer_base import BaseFix
from lib2to3.pytree import Node


class FixPathsNested(BaseFix):
    BM_compatible = True

    PATTERN = """
    power < 'Path' trailer < '(' a=power < 'Path' trailer < '(' any ')' > trailer < '.' any > [ trailer < '(' any* ')' > ] > ')' > b=trailer < '.' any > [ c=trailer < '(' any* ')' > ] >
    |
    power < 'Path' d=trailer < '(' term < power < 'Path' trailer < '(' any ')' > > [ '/' any* ]  > ')' > e=trailer < '.' any > f=trailer < '(' any* ')' > > 
    """

    def transform(self, node: Node, results):
        if "a" in results:
            n = results["a"]
            n.prefix = node.prefix
            n.append_child(results["b"])
            if "c" in results:
                n.append_child(results["c"])
        elif "d" in results:
            n = results["d"]
            n.prefix = node.prefix
            n.append_child(results["e"])
            n.append_child(results["f"])
        else:
            raise ValueError("Not ok")
        return n
