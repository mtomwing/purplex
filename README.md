# purplex

A set of wrappers and other tools that make it easier to work with PLY.

  * **Lexer**: a pure-python lexer that can be used as a drop-in replacement with PLY.
  * **Parser**: a wrapper around PLY's yacc parser that provides a more pythonic interface.

## Requirements

  * Python 3.2+
  * ply 3.4

## Testing

`python3 setup.py test`

## Installation

`python3 setup.py install`

## Example: Simple Expression Evaluator

```python
from purplex import Lexer, TokenDef
from purplex import Parser, attach


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
    PRECEDENCE = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
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

    @attach('e : INTEGER')
    def number(self, num):
        return int(num)


if __name__ == '__main__':
    parser = MyParser()
    # Should return 10 if precedence is working
    print(parser.parse('2 + 3 * 4 - 4'))
```

```bash
$ python example.py
10
```
