from purplex import Lexer, TokenDef
from purplex import Parser, attach
from purplex import LEFT, RIGHT


class MyLexer(Lexer):

    INTEGER = TokenDef(r'\d+')

    LPAREN = TokenDef(r'\(')
    RPAREN = TokenDef(r'\)')

    TIMES = TokenDef(r'\*')
    DIVIDE = TokenDef(r'/')
    PLUS = TokenDef(r'\+')
    MINUS = TokenDef(r'-')

    WHITESPACE = TokenDef(r'[\s\n]+', ignore=True)


class MyParser(Parser):

    LEXER = MyLexer
    START = 'e'

    PRECEDENCE = (
        (RIGHT, 'UMINUS'),
        (LEFT, 'TIMES', 'DIVIDE'),
        (LEFT, 'PLUS', 'MINUS'),
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


if __name__ == '__main__':
    parser = MyParser()
    problems = [
        ('2 + 3 * 4 - 4', 10),
        ('-4', -4),
        ('-4 * 2', -8),
        ('-2 * - (1 + 1)', 4),
        ('6 / 2 * 4 - 8 * 1', 4),
    ]
    for problem, answer in problems:
        result = parser.parse(problem)
        print(problem, '=', result, ';', result == answer)
