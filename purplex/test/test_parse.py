import pytest

from purplex import exception
from purplex.lex import Lexer, TokenDef
from purplex.parse import ParserBase, Parser, attach


class SimpleExprLexer(Lexer):

    INTEGER = TokenDef(r'\d+')

    LPAREN = TokenDef(r'\(')
    RPAREN = TokenDef(r'\)')

    TIMES = TokenDef(r'\*')
    DIVIDE = TokenDef(r'/')
    PLUS = TokenDef(r'\+')
    MINUS = TokenDef(r'-')

    WHITESPACE = TokenDef(r'[\s\n]+', ignore=True)


def test_table_conflict():
    noop = lambda *args: args
    attrs = {
        'LEXER': SimpleExprLexer,
        'START': 'e',

        'brackets': attach('e : LPAREN e RPAREN')(noop),
        'addition': attach('e : e PLUS e')(noop),
        'subtract': attach('e : e MINUS e')(noop),
        'multiply': attach('e : e TIMES e')(noop),
        'division': attach('e : e DIVIDE e')(noop),
        'number': attach('e : INTEGER')(noop),
    }

    with pytest.raises(exception.TableConflictError):
        ParserBase.__new__(ParserBase, 'SimpleExprParser', (Parser,), attrs)


def test_basic_no_conflict():
    class SimpleExprParser(Parser):

        LEXER = SimpleExprLexer
        START = 's'

        @attach('s : s PLUS p')
        def sums_plus(self, *args):
            return args[0] + args[2]

        @attach('p : p TIMES v')
        def products_times(self, *args):
            return args[0] * args[2]

        @attach('s : p')
        @attach('p : v')
        def noop(self, *args):
            return args[0]

        @attach('v : INTEGER')
        def value(self, *args):
            return int(args[0])

    parser = SimpleExprParser()
    assert parser.parse('2 + 2 * 4') == 10
    assert parser.parse('5 * 2 + 2') == 12
