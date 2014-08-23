import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Node(object):
    @abc.abstractmethod
    def pretty(self):
        return ''


class ListNode(Node):
    def __init__(self):
        self.children = []

    def __iter__(self):
        return iter(self.children)

    def __len__(self):
        return len(self.children)

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
