class TokenMatchesEmptyStringError(Exception):
    '''Raised when TokenDef regex matches the empty string.'''

    def __init__(self, regexp):
        message = 'token {!r} matched the empty string'.format(regexp)
        super(TokenMatchesEmptyStringError, self).__init__(message)
