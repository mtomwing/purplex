# purplex
[![Build Status][build-status-badge]] [build-status]
[![Coverage Status][coverage-status-badge]] [coverage-status]
[![PyPi version][pypi-version-badge]] [pypi-version]
[![PyPi downloads][pypi-downloads-badge]] [pypi-downloads]

A pure-Python lexer and parser. Together they provide an experience reminiscent of `yacc` or `bison`, but of course in a more Pythonic way.

NOTE: As of the parser rewrite, only "small" grammars are supported. In the future I hope to improve this by using LALR(1) instead of LR(1) for the parsing table generation.


## History

This project started out as a way to avoid writing C++ for a compilers class. Since I didn't know much about parsing algorithms at the time, it was simply intended to provide a nicer interface to PLY. After the class was over I took some time to tidy it up and add the textbook (basically straight out of the Dragon Book) LR(1) parsing algorithm.

I use purplex myself for one-off scripts here and there. However to date, the only project using purplex for anything big is [hangups](https://github.com/tdryer/hangups).


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
[pypi-version-badge]: https://img.shields.io/pypi/v/purplex.svg
[pypi-downloads]: https://crate.io/packages/purplex "Number of downloads from PyPi"
[pypi-downloads-badge]: https://img.shields.io/pypi/dm/purplex.svg
