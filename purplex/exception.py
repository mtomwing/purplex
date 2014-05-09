class TokenMatchesEmptyStringError(Exception):
    '''Raised when TokenDef regex matches the empty string.'''

    def __init__(self, regexp):
        message = 'token {!r} matched the empty string'.format(regexp)
        super(TokenMatchesEmptyStringError, self).__init__(message)


class NoMatchingTokenFoundError(Exception):
    '''Raised when a Lexer cannot match a TokenDef to the input data.'''

    def __init__(self, data):
        message = 'No token definition matched: {!r}'.format(data)
        super(NoMatchingTokenFoundError, self).__init__(message)
