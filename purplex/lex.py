import collections

from purplex.exception import NoMatchingTokenFoundError
from purplex.token import TokenDef
from purplex.token import Token


class LexerBase(type):
    @classmethod
    def __prepare__(metacls, name, bases):
        return collections.OrderedDict()

    def __new__(cls, name, bases, dct):
        tokens = collections.OrderedDict()
        for name, attr in dct.items():
            if isinstance(attr, TokenDef):
                tokens[name] = attr
                del dct[name]
        ret = super(LexerBase, cls).__new__(cls, name, bases, dct)
        if hasattr(ret, 'tokens'):
            tokens.update(ret.tokens)
        ret.tokens = tokens
        return ret


class Lexer(metaclass=LexerBase):
    def __init__(self, input_text):
        self.input_text = input_text
        self.input_pos = 0
        self.line_num = 1
        self.line_pos = 1

    def __iter__(self):
        while not self.done():
            ret = self.next_token()
            if ret is not None:
                yield ret

    def consume(self, token):
        self.input_pos += len(token)
        self.line_num += token.value.count('\n')

        newline_idx = token.value.rfind('\n')
        if newline_idx >= 0:
            self.line_pos = len(token.value) - newline_idx
        else:
            self.line_pos += len(token.value)

    def next_token(self):
        matches = []

        for name, token_defn in self.tokens.items():
            match = token_defn.regexp.match(self.input_text, self.input_pos)
            if match:
                token = Token(name, match.group(0), token_defn,
                              self.line_num, self.line_pos)
                matches.append(token)

        s_matches = sorted(matches, key=lambda t: len(t), reverse=True)

        if s_matches:
            token = s_matches[0]
            self.consume(token)

            if hasattr(self, 'on_{}'.format(token.name)):
                getattr(self, 'on_{}'.format(token.name))(token)

            self.on_token(token)

            if token.defn.ignore:
                return None
            else:
                return token
        else:
            raise NoMatchingTokenFoundError(
                self.line_num,
                self.line_pos,
                self.input_text[self.input_pos:self.input_pos + 10],
            )

    def done(self):
        return self.input_pos >= len(self.input_text)

    # Override these

    def on_token(self, token):
        pass
