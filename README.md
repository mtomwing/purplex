purplex
=======

Pure python lexer implementation. It's somewhat designed to be a drop-in replacement for PLY's lexer that does longest token matching.

Example Usage
-------------

```python
from purplex import Lexer, TokenDef


class MyLexer(Lexer):
    IDENTIFIER = TokenDef(r'[a-zA-Z_][a-zA-Z_0-9]*')
    INTEGER = TokenDef(r'[0-9]+')
    

if __name__ == '__main__':
    lexer = MyLexer('my_variable123')
    for token in lexer:
        print(token.name, ':', repr(token.value))
```

```bash
$ python example.py
IDENTIFIER : 'my_variable123'
```
