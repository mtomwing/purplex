import collections

EPSILON = '<empty>'
END_OF_INPUT = '<$>'


class Production(object):
    """Represents a grammar production rule."""

    def __init__(self, rule, func):
        items = rule.split(':', 1)
        self.lhs = items[0].strip()
        self.rhs = items[1].strip().split() or [EPSILON]
        self.func = func

        self._str = '{} : {}'.format(self.lhs, ' '.join(self.rhs))
        self._len = len(self.rhs) - int(EPSILON in self.rhs)

    def __str__(self):
        return self._str

    def __repr__(self):
        return repr(self._str)

    def __hash__(self):
        return hash(self._str)

    def __len__(self):
        return self._len


class DottedRule(object):
    """Represents a "dotted rule" during closure construction."""

    def __init__(self, production, pos, lookahead):
        self.production = production
        self.pos = pos
        self.lookahead = lookahead

        self._str = '[{} : {} . {}, {}]'.format(
            self.production.lhs,
            ' '.join(self.production.rhs[:self.pos]),
            ' '.join(self.production.rhs[self.pos:]),
            self.lookahead,
        )
        self.at_end = self.pos == len(self.production.rhs)
        self.rest = self.production.rhs[self.pos + 1:] + [self.lookahead]

    def __hash__(self):
        return hash(self._str)

    def __repr__(self):
        return repr(self._str)

    def __eq__(self, other):
        return self.production == other.production and self.pos == other.pos

    def __len__(self):
        return len(self.production)

    @property
    def lhs(self):
        return self.production.lhs

    @property
    def rhs(self):
        return self.production.rhs

    def move_dot(self):
        """Returns the DottedRule that results from moving the dot."""
        return self.__class__(self.production, self.pos + 1, self.lookahead)


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

    def initial_closure(self):
        """Computes the initial closure using the START_foo production."""
        first_rule = DottedRule(self.start, 0, END_OF_INPUT)
        return self.closure([first_rule])

    def goto(self, rules, symbol):
        """Computes the next closure for rules based on the symbol we got.

        Args:
            rules - an iterable of DottedRules
            symbol - a string denoting the symbol we've just seen

        Returns: frozenset of DottedRules
        """
        return self.closure(
            {rule.move_dot() for rule in rules
             if not rule.at_end and rule.rhs[rule.pos] == symbol},
        )

    def closure(self, rules):
        """Fills out the entire closure based on some initial dotted rules.

        Args:
            rules - an iterable of DottedRules

        Returns: frozenset of DottedRules

        """
        closure = set()

        todo = set(rules)
        while todo:
            rule = todo.pop()
            closure.add(rule)

            # If the dot is at the end, there's no need to process it.
            if rule.at_end:
                continue

            symbol = rule.rhs[rule.pos]
            for production in self.nonterminals[symbol]:
                for first in self.first(rule.rest):
                    if EPSILON in production.rhs:
                        # Move immediately to the end if the production
                        # goes to epsilon
                        new_rule = DottedRule(production, 1, first)
                    else:
                        new_rule = DottedRule(production, 0, first)

                    if new_rule not in closure:
                        todo.add(new_rule)

        return frozenset(closure)

    def closures(self):
        """Computes all LR(1) closure sets for the grammar."""
        initial = self.initial_closure()
        closures = collections.OrderedDict()
        goto = collections.defaultdict(dict)

        todo = set([initial])
        while todo:
            closure = todo.pop()
            closures[closure] = closure

            symbols = {rule.rhs[rule.pos] for rule in closure
                       if not rule.at_end}
            for symbol in symbols:
                next_closure = self.goto(closure, symbol)

                if next_closure in closures or next_closure in todo:
                    next_closure = (closures.get(next_closure)
                                    or todo.get(next_closure))
                else:
                    closures[next_closure] = next_closure
                    todo.add(next_closure)

                goto[closure][symbol] = next_closure

        return initial, closures, goto
