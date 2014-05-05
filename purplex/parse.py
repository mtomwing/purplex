import functools
import logging

from ply import yacc


def attach(production):
    def wrapper(func):
        if not hasattr(func, '_productions'):
            func._productions = []
        func._productions.append(production)
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


class MagicParser(object):
    def add(self, parser, production, node_cls):
        def p_something(t):
            nargs = len(t.slice)
            t[0] = node_cls(parser, *[t[i] for i in range(1, nargs)])
        func_name = 'p_{}_{}{}'.format(production.split()[0],
                                       node_cls.__name__,
                                       abs(hash(production)))
        p_something.__name__ = func_name
        setattr(self, func_name, p_something)
        getattr(self, func_name).__doc__ = production


class ParserBase(type):
    def __new__(cls, name, bases, dct):
        productions = {}

        for _, attr in dct.items():
            if hasattr(attr, '_productions'):
                for production in attr._productions:
                    productions[production] = attr

        ret = type.__new__(cls, name, bases, dct)
        if not hasattr(ret, '_productions'):
            ret._productions = {}
        productions.update(ret._productions)
        ret._productions = productions
        return ret


class Parser(metaclass=ParserBase):
    LEXER = None
    PRECEDENCE = []

    @classmethod
    def attach(cls, production):
        def wrapper(node_cls):
            cls._productions[production] = node_cls
            return node_cls
        return wrapper

    def __init__(self, start=None, debug=False):
        self._parser = self._build(start, debug)
        self._lexer = None

    def _build(self, start, debug):
        magic = MagicParser()
        magic.tokens = [name for name, tokendef in self.LEXER.tokens.items()
                        if not tokendef.ignore]
        if self.PRECEDENCE:
            magic.precedence = self.PRECEDENCE

        for production, node_cls in self._productions.items():
            magic.add(self, production, node_cls)
        setattr(magic, 'p_error', self.on_error)

        error_logger = logging.getLogger('{}.{}'
                                         .format(self.__module__,
                                                 self.__class__.__name__))
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        error_logger.addHandler(handler)

        debug_logger = error_logger if debug else yacc.NullLogger()

        if debug:
            error_logger.setLevel(logging.DEBUG)
            self.debug = error_logger
        else:
            error_logger.setLevel(logging.ERROR)
            self.debug = False

        return yacc.yacc(module=magic, start=start,
                         write_tables=False, debug=debug,
                         debuglog=debug_logger, errorlog=error_logger)

    def parse(self, input_stream):
        self.lexer = self.LEXER(input_stream)

        def tokens():
            for token in self.lexer:
                yield token
            yield None

        token_gen = tokens()

        return self._parser.parse(lexer=self.lexer,
                                  tokenfunc=functools.partial(next, token_gen),
                                  debug=self.debug)

    # Implement these if you want:

    def on_error(self, p):
        '''
        Is called when PLY's yacc encounters a parsing error.
        '''
        pass
