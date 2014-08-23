import re

from purplex.exception import TokenMatchesEmptyStringError


class TokenDef(object):

    NEXT_NUM = 0

    def __init__(self, regexp, ignore=False):
        self.regexp = re.compile(regexp, re.UNICODE)
        self.ignore = ignore

        # Make sure it doesn't match the empty string
        if self.regexp.match(''):
            raise TokenMatchesEmptyStringError(regexp)

        self.num = TokenDef.NEXT_NUM
        TokenDef.NEXT_NUM += 1

    def __lt__(self, other):
        return self.num < other.num


class Token(object):
    def __init__(self, name, value, defn, line_num, line_pos):
        self.name = name
        self.value = value
        self.defn = defn
        self.line_num = line_num
        self.line_pos = line_pos

        # For compatibility with yacc
        self.type = name

    def __str__(self):
        return '{}({})<line {}, col {}>'.format(self.name, repr(self.value),
                                                self.line_num, self.line_pos)

    def __len__(self):
        return len(self.value)
