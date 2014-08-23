import collections
import itertools

import six

from purplex.exception import TableConflictError, StartSymbolNotReducedError
from purplex.grammar import Grammar, Production, END_OF_INPUT
from purplex.lex import Lexer
from purplex.token import Token

END_OF_INPUT_TOKEN = Token(END_OF_INPUT, '', '', 0, 0)

LEFT = 'left'
RIGHT = 'right'
DEFAULT_PREC = (LEFT, 0)


def attach(rule, prec_symbol=None):
    def wrapper(func):
        if not hasattr(func, 'productions'):
            func.productions = set()
        func.productions.add((Production(rule, func), prec_symbol))
        return func
    return wrapper


def attach_list(nonterminal, singular, single=True, epsilon=False):
    def wrapper(func):
        productions = [
            '{} : {} {}'.format(nonterminal, nonterminal, singular),
        ]
        if single:
            productions.append('{} : {}'.format(nonterminal, singular))
        if epsilon:
            productions.append('{} : '.format(nonterminal))

        for production in productions:
            attach(production)(func)
        return func
    return wrapper


def attach_sep_list(nonterminal, singular, separator, epsilon=False):
    def wrapper(func):
        inner_nonterminal = '{}_inner'.format(nonterminal)
        productions = [
            '{} : {}'.format(nonterminal, inner_nonterminal),
            '{} : {} {} {}'.format(inner_nonterminal, inner_nonterminal,
                                   separator, singular),
            '{} : {}'.format(inner_nonterminal, singular),
            ]
        if epsilon:
            productions.append('{} : '.format(nonterminal))

        for producution in productions:
            attach(producution)(func)
        return func
    return wrapper


class ParserBase(type):

    def __new__(cls, name, bases, dct):
        productions = set()
        for _, attr in dct.items():
            if hasattr(attr, 'productions'):
                productions |= attr.productions

        grammar = Grammar(dct['LEXER'].token_map.keys(),
                          [production for production, _ in productions],
                          start=dct['START'])
        precedence = cls.compute_precedence(grammar.terminals,
                                            productions,
                                            dct.get('PRECEDENCE') or ())
        INITIAL_STATE, ACTION, GOTO = cls.make_tables(grammar, precedence)
        dct.update({
            'grammar': grammar,
            'INITIAL_STATE': INITIAL_STATE,
            'ACTION': ACTION,
            'GOTO': GOTO,
        })
        return type.__new__(cls, name, bases, dct)

    @staticmethod
    def compute_precedence(terminals, productions, precedence_levels):
        """Computes the precedence of terminal and production.

        The precedence of a terminal is it's level in the PRECEDENCE tuple. For
        a production, the precedence is the right-most terminal (if it exists).
        The default precedence is DEFAULT_PREC - (LEFT, 0).

        Returns:
            precedence - dict[terminal | production] = (assoc, level)

        """
        precedence = collections.OrderedDict()

        for terminal in terminals:
            precedence[terminal] = DEFAULT_PREC

        level_precs = range(len(precedence_levels), 0, -1)
        for i, level in zip(level_precs, precedence_levels):
            assoc = level[0]
            for symbol in level[1:]:
                precedence[symbol] = (assoc, i)

        for production, prec_symbol in productions:
            if prec_symbol is None:
                prod_terminals = [symbol for symbol in production.rhs
                                  if symbol in terminals] or [None]
                precedence[production] = precedence.get(prod_terminals[-1],
                                                        DEFAULT_PREC)
            else:
                precedence[production] = precedence.get(prec_symbol,
                                                        DEFAULT_PREC)

        return precedence

    @staticmethod
    def make_tables(grammar, precedence):
        """Generates the ACTION and GOTO tables for the grammar.

        Returns:
            action - dict[state][lookahead] = (action, ...)
            goto - dict[state][just_reduced] = new_state

        """
        ACTION = {}
        GOTO = {}

        labels = {}

        def get_label(closure):
            if closure not in labels:
                labels[closure] = len(labels)
            return labels[closure]

        def resolve_shift_reduce(lookahead, s_action, r_action):
            s_assoc, s_level = precedence[lookahead]
            r_assoc, r_level = precedence[r_action[1]]

            if s_level < r_level:
                return r_action
            elif s_level == r_level and r_assoc == LEFT:
                return r_action
            else:
                return s_action

        initial, closures, goto = grammar.closures()
        for closure in closures:
            label = get_label(closure)

            for rule in closure:
                new_action, lookahead = None, rule.lookahead

                if not rule.at_end:
                    symbol = rule.rhs[rule.pos]
                    is_terminal = symbol in grammar.terminals
                    has_goto = symbol in goto[closure]
                    if is_terminal and has_goto:
                        next_state = get_label(goto[closure][symbol])
                        new_action, lookahead = ('shift', next_state), symbol
                elif rule.production == grammar.start and rule.at_end:
                    new_action = ('accept',)
                elif rule.at_end:
                    new_action = ('reduce', rule.production)

                if new_action is None:
                    continue

                prev_action = ACTION.get((label, lookahead))
                if prev_action is None or prev_action == new_action:
                    ACTION[label, lookahead] = new_action
                else:
                    types = (prev_action[0], new_action[0])
                    if types == ('shift', 'reduce'):
                        chosen = resolve_shift_reduce(lookahead,
                                                      prev_action,
                                                      new_action)
                    elif types == ('reduce', 'shift'):
                        chosen = resolve_shift_reduce(lookahead,
                                                      new_action,
                                                      prev_action)
                    else:
                        raise TableConflictError(prev_action, new_action)

                    ACTION[label, lookahead] = chosen

            for symbol in grammar.nonterminals:
                if symbol in goto[closure]:
                    GOTO[label, symbol] = get_label(goto[closure][symbol])

        return get_label(initial), ACTION, GOTO


@six.add_metaclass(ParserBase)
class Parser(object):

    LEXER = Lexer
    START = 'S'
    PRECEDENCE = ()

    grammar = None
    INITIAL_STATE = 0
    ACTION = {}
    GOTO = {}

    def parse(self, raw):
        """Parses an input string and applies the parser's grammar."""
        lexer = self.LEXER(raw)
        tokens = iter(itertools.chain(lexer, [END_OF_INPUT_TOKEN]))
        stack = [(self.INITIAL_STATE, '<initial>', '<begin>')]

        token = next(tokens)
        while stack:
            state, _, _ = stack[-1]

            action = self.ACTION.get((state, token.name))
            if action is None:
                raise StartSymbolNotReducedError(self.START)

            if action[0] == 'reduce':
                production = action[1]

                # Special case for epsilon rules
                if len(production):
                    args = (item[2] for item in stack[-len(production):])
                    del stack[-len(production):]
                else:
                    args = []

                prev_state, _, _ = stack[-1]
                new_state = self.GOTO[prev_state, production.lhs]
                stack.append((
                    new_state,
                    production.lhs,
                    production.func(self, *args),
                ))
            elif action[0] == 'shift':
                stack.append((action[1], token.name, token.value))
                token = next(tokens)
            elif action[0] == 'accept':
                return stack[-1][2]
