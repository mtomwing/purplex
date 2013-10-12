class Node(object):
    def __init__(self, parser, *args):
        self.parser = parser
        self.children = args

    def __repr__(self):
        return '{}{}'.format(self.__class__.__name__, repr(self.children))


class ListNode(Node):
    def __init__(self):
        self.children = []

    def __iter__(self):
        return iter(self.children)

    def add(self, child):
        self.children.append(child)


def auto_collect(node_cls, children):
    if len(children) > 1:
        children[0].add(children[-1])
        return children[0]
    elif len(children) == 1:
        if isinstance(children[0], node_cls):
            return children[0]
        else:
            ret = node_cls()
            ret.add(children[0])
            return ret
    else:
        return node_cls()
