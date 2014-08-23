# purplex
[![Build Status][build-status-badge]] [build-status]
[![Coverage Status][coverage-status-badge]] [coverage-status]
[![PyPi version][pypi-version-badge]] [pypi-version]
[![PyPi downloads][pypi-downloads-badge]] [pypi-downloads]

A set of wrappers and other tools that make it easier to work with PLY.

  * **Lexer**: a pure-python lexer that can be used as a drop-in replacement with PLY.
  * **Parser**: a pure-python LR(1) parser with support for precedence

NOTE: As of the parser rewrite, only "small" grammars are supported. In the future I hope to improve this by using LALR(1) instead of LR(1).


## Requirements

  * Python 2.7 or 3+
  * requirements.txt


## Testing

`python setup.py test`


## Example: Simple Expression Evaluator

```python
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
```

```bash
$ python example.py
2 + 3 * 4 - 4 = 10 ; True
-4 = -4 ; True
-4 * 2 = -8 ; True
-2 * - (1 + 1) = 4 ; True
6 / 2 * 4 - 8 * 1 = 4.0 ; True
```

[build-status]: https://travis-ci.org/mtomwing/purplex "Build status"
[build-status-badge]: https://travis-ci.org/mtomwing/purplex.png?branch=master
[coverage-status]: https://coveralls.io/r/mtomwing/purplex "Test coverage"
[coverage-status-badge]: https://coveralls.io/repos/mtomwing/purplex/badge.png?branch=master
[pypi-version]: https://crate.io/packages/purplex "Latest version hosted on PyPi"
[pypi-version-badge]: https://pypip.in/v/purplex/badge.png
[pypi-downloads]: https://crate.io/packages/purplex "Number of downloads from PyPi"
[pypi-downloads-badge]: https://pypip.in/d/purplex/badge.png
