import pytest

from purplex.common import OrderedSet


def test_ordered_set():
    items = [
        '3',
        '2',
        '1',
    ]
    ordered_set = OrderedSet(items)

    # Ordering should be preserved
    assert list(ordered_set) == items

    # __contains__ should work
    for item in items:
        assert item in ordered_set

    # Add a new item
    ordered_set.add('4')
    assert '4' in ordered_set

    # Remove an item
    ordered_set.remove('3')
    assert '3' not in ordered_set

    # Get a list of all items
    copy = ordered_set.items()
    assert copy == ordered_set._dict.keys()
