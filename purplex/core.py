import collections

from purplex.token import TokenDef
from purplex.token import Token


class LexerBase(type):
    @classmethod
    def __prepare__(metacls, name, bases):
        return collections.OrderedDict()

    def __new__(cls, name, bases, dct):
        new_dct = {}
        tokens = collections.OrderedDict()
        for name, attr in dct.items():
            if isinstance(attr, TokenDef):
                tokens[name] = attr
            else:
                new_dct[name] = attr
        new_dct['tokens'] = tokens
        return type.__new__(cls, name, bases, new_dct)


class Lexer(metaclass=LexerBase):
    def __init__(self, input_text):
        self.input_text = input_text
        self.input_pos = 0

    def __iter__(self):
        while not self.done():
            yield self.token()

    def consume(self, n):
        self.input_pos += n

    def token(self):
        matches = []
        for name, token_defn in self.tokens.items():
            match = token_defn.regexp.match(self.input_text, self.input_pos)
            if match:
                token = Token(name, match.group(0), token_defn)
                matches.append(token)

        s_matches = sorted(matches, key=lambda t: len(t), reverse=True)

        if s_matches:
            token = s_matches[0]
            self.consume(len(token))
            if hasattr(self, 'on_{}'.format(token.name)):
                getattr(self, 'on_{}'.format(token.name))(token)
            return token
        else:
            raise Exception('No token definition matched: "{}"'.format(self.input_text[self.input_pos]))

    def done(self):
        return self.input_pos >= len(self.input_text)
