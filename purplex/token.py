import re


class TokenDef(object):
    def __init__(self, regexp):
        self.regexp = re.compile(regexp)


class Token(object):
    def __init__(self, name, value, defn):
        self.name = name
        self.value = value
        self.defn = defn

    def __len__(self):
        return len(self.value)
