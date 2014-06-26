import collections

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
        self.start_symbol = 'START_{}'.format(start)
        self.start = Production("{} : {}".format(self.start_symbol, start),
                                lambda a: a)
        self.nonterminals[self.start_symbol].add(self.start)

        self._first = collections.defaultdict(set)
        self._compute_first()
        self._follow = collections.defaultdict(set)
        self._compute_follow()

    def first(self, symbols):
        """Computes the intermediate FIRST set using symbols."""
        ret = set()

        if EPSILON in symbols:
            return set([EPSILON])

        for symbol in symbols:
            ret |= self._first[symbol] - set([EPSILON])
            if EPSILON not in self._first[symbol]:
                break
        else:
            ret.add(EPSILON)

        return ret

    def _compute_first(self):
        """Computes the FIRST set for every symbol in the grammar.

        Tenatively based on _compute_first in PLY.
        """
        for terminal in self.terminals:
            self._first[terminal].add(terminal)
        self._first[END_OF_INPUT].add(END_OF_INPUT)

        while True:
            changed = False

            for nonterminal, productions in self.nonterminals.items():
                for production in productions:
                    new_first = self.first(production.rhs)
                    if new_first - self._first[nonterminal]:
                        self._first[nonterminal] |= new_first
                        changed = True

            if not changed:
                break

    def _compute_follow(self):
        """Computes the FOLLOW set for every non-terminal in the grammar.

        Tenatively based on _compute_follow in PLY.
        """
        self._follow[self.start_symbol].add(END_OF_INPUT)

        while True:
            changed = False

            for nonterminal, productions in self.nonterminals.items():
                for production in productions:
                    for i, symbol in enumerate(production.rhs):
                        if symbol not in self.nonterminals:
                            continue

                        first = self.first(production.rhs[i + 1:])
                        new_follow = first - set([EPSILON])
                        if EPSILON in first or i == (len(production.rhs) - 1):
                            new_follow |= self._follow[nonterminal]

                        if new_follow - self._follow[symbol]:
                            self._follow[symbol] |= new_follow
                            changed = True

            if not changed:
                break
