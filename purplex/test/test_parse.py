import pytest

from purplex import Lexer, TokenDef, Parser, attach, exception


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
    with pytest.raises(exception.TableConflictError):
        class SimpleExprParser(Parser):

            LEXER = SimpleExprLexer
            START = 'e'

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

            @attach('e : INTEGER')
            def number(self, num):
                return int(num)


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
