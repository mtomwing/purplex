from ply import yacc


class Node(object):
    def __init__(self, *args):
        pass


class MagicParser(object):
    def add(self, production, node_cls):
        def p_something(t):
            nargs = len(production.split()) - 2
            t[0] = node_cls(*[t[i] for i in range(1, nargs + 1)])
        func_name = 'p_{}_{}'.format(production.split()[0], node_cls.__name__)
        setattr(self, func_name, p_something)
        getattr(self, func_name).__doc__ = production


class ParserBase(type):
    def __new__(cls, name, bases, dct):
        dct['_productions'] = {}
        return type.__new__(cls, name, bases, dct)


class Parser(metaclass=ParserBase):
    LEXER = None

    @classmethod
    def attach(cls, production):
        def wrapper(node_cls):
            cls._productions[production] = node_cls
            return node_cls
        return wrapper

    def __init__(self):
        self._parser = self._build()

    def _build(self):
        magic = MagicParser()
        magic.tokens = list(self.LEXER.tokens.keys())

        print(magic.tokens)

        for production, node_cls in self._productions.items():
            magic.add(production, node_cls)

        return yacc.yacc(module=magic, write_tables=False)

    def parse(self, input_stream):
        lexer = self.LEXER(input_stream)
        return self._parser.parse(lexer=lexer)
