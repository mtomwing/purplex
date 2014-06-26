import collections


class OrderedSet(object):
    """An ordered set."""

    def __init__(self, initial=None):
        """
        Args:
            initial - an iterable of initial items for the set

        """
        self._dict = collections.OrderedDict()
        if initial:
            for item in initial:
                self.add(item)

    def __contains__(self, item):
        return item in self._dict

    def __iter__(self):
        return iter(self._dict)

    def add(self, item):
        """Add an item to the set."""
        self._dict[item] = None

    def remove(self, item):
        """Remove an item from the set."""
        del self._dict[item]

    def items(self):
        """Get a list of all items in the set."""
        return self._dict.keys()
