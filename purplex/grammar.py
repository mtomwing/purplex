import collections
import functools

EPSILON = '<empty>'
END_OF_INPUT = '<$>'


class Production(object):
    """Represents a grammar production rule."""

    def __init__(self, rule, func):
        items = rule.split(':', 1)
        self.lhs = items[0].strip()
        self.rhs = items[1].strip().split()
        self.func = func

    def __str__(self):
        return '{} : {}'.format(self.lhs, ' '.join(self.rhs))

    def __hash__(self):
        return hash(str(self))


class Grammar(object):
    """Represents a context-free grammar."""

    def __init__(self, terminals, productions, start):
        self.terminals = set(terminals)
        self.nonterminals = collections.defaultdict(set)
        for production in productions:
            self.nonterminals[production.lhs].add(production)

        # Augment the grammar to have a definite start symbol
        self.start = 'START_{}'.format(start)
        self.nonterminals[self.start].add(
            Production("{} : {}".format(self.start, start), lambda a: a)
        )

        self.first = self._compute_first()
        self.follow = self._compute_follow()

    @staticmethod
    def _first(symbols, first):
        """Computes the intermediate FIRST set using symbols."""
        ret = set()

        if EPSILON in symbols:
            return set([EPSILON])

        for symbol in symbols:
            ret |= first[symbol] - set([EPSILON])
            if EPSILON not in first[symbol]:
                break
        else:
            ret.add(EPSILON)

        return ret

    def _compute_first(self):
        """Computes the FIRST set for every symbol in the grammar.

        Tenatively based on _compute_first in PLY.
        """
        first = collections.defaultdict(set)
        _first = functools.partial(self._first, first=first)

        for terminal in self.terminals:
            first[terminal].add(terminal)
        first[END_OF_INPUT].add(END_OF_INPUT)

        while True:
            changed = False

            for nonterminal, productions in self.nonterminals.items():
                for production in productions:
                    new_first = _first(production.rhs)
                    if new_first - first[nonterminal]:
                        first[nonterminal] |= new_first
                        changed = True

            if not changed:
                break

        return first

    def _compute_follow(self):
        """Computes the FOLLOW set for every non-terminal in the grammar.

        Tenatively based on _compute_follow in PLY.
        """
        follow = collections.defaultdict(set)
        follow[self.start].add(END_OF_INPUT)
        _first = functools.partial(self._first, first=self.first)

        while True:
            changed = False

            for nonterminal, productions in self.nonterminals.items():
                for production in productions:
                    for i, symbol in enumerate(production.rhs):
                        if symbol not in self.nonterminals:
                            continue

                        first = _first(production.rhs[i + 1:])
                        new_follow = first - set([EPSILON])
                        if EPSILON in first or i == (len(production.rhs) - 1):
                            new_follow |= follow[nonterminal]

                        if new_follow - follow[symbol]:
                            follow[symbol] |= new_follow
                            changed = True

            if not changed:
                break

        return follow
