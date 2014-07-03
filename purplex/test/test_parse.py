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

        'm': attach('m : e INTEGER')(noop),
        'e_a': attach('e : a')(noop),
        'e_b': attach('e : b')(noop),
        'a': attach('a : ')(noop),
        'b': attach('b : ')(noop),
    }

    with pytest.raises(exception.TableConflictError):
        ParserBase.__new__(ParserBase, 'SimpleExprParser', (Parser,), attrs)


def test_basic_no_conflict():
    class SimpleExprParser(Parser):

        LEXER = SimpleExprLexer
        START = 'e'

        PRECEDENCE = (
            ('right', 'UMINUS'),
            ('left', 'TIMES', 'DIVIDE'),
            ('left', 'PLUS', 'MINUS'),
        )

        @attach('e : LPAREN e RPAREN')
        def brackets(self, lparen, expr, rparen):
            return expr

        @attach('e : e PLUS e')
        def addition(self, left, op, right):
            return left + right

        @attach('e : e MINUS e')
        def subtract(self, left, op, right):
            return left - right

        @attach('e : e TIMES e')
        def multiply(self, left, op, right):
            return left * right

        @attach('e : e DIVIDE e')
        def division(self, left, op, right):
            return left / right

        @attach('e : MINUS e', prec_symbol='UMINUS')
        def negate(self, minus, expr):
            return -expr

        @attach('e : INTEGER')
        def number(self, num):
            return int(num)

    parser = SimpleExprParser()
    assert parser.parse('2 + 3 * 4 - 4') == 10
    assert parser.parse('-4') == -4
    assert parser.parse('-4 * 2') == -8
    assert parser.parse('-2 * - (1 + 1)') == 4
    assert parser.parse('6 / 2 * 4 - 8 * 1') == 4
