from operator import itemgetter
import collections

import six

from purplex.exception import NoMatchingTokenFoundError
from purplex.token import TokenDef
from purplex.token import Token


class LexerBase(type):

    def __new__(cls, name, bases, dct):
        ret = super(LexerBase, cls).__new__(cls, name, bases, dct)

        # Collect all TokenDefs
        tokens = sorted(((name, attr) for name, attr in dct.items()
                         if isinstance(attr, TokenDef)), key=itemgetter(1))
        token_map = collections.OrderedDict(tokens)

        # Inherit TokenDefs from any base classes
        if hasattr(ret, 'token_map'):
            token_map.update(ret.token_map)

        ret.token_map = token_map
        ret.tokens = list(token_map.items())
        return ret


@six.add_metaclass(LexerBase)
class Lexer(object):
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

        for name, token_defn in self.tokens:
            match = token_defn.regexp.match(self.input_text, self.input_pos)
            if match:
                token = Token(name, match.group(0), token_defn,
                              self.line_num, self.line_pos)
                matches.append(token)

        if matches:
            token = max(matches, key=len)
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
