class PurplexError(Exception):
    pass


class TokenMatchesEmptyStringError(PurplexError):
    '''Raised when TokenDef regex matches the empty string.'''

    def __init__(self, regexp):
        message = 'token {!r} matched the empty string'.format(regexp)
        super(TokenMatchesEmptyStringError, self).__init__(message)


class NoMatchingTokenFoundError(PurplexError):
    '''Raised when a Lexer cannot match a TokenDef to the input data.'''

    def __init__(self, line_num, line_pos, data):
        message = ('No token definition matched @ line {} position {}: {!r}'
                   .format(line_num, line_pos, data + '...'))
        super(NoMatchingTokenFoundError, self).__init__(message)


class TableConflictError(PurplexError):
    '''Raised when a Parser would overwrite an action in the action table.'''

    def __init__(self, prev_action, new_action):
        message = 'Tried to replace {} with {}'.format(prev_action, new_action)
        super(TableConflictError, self).__init__(message)


class StartSymbolNotReducedError(PurplexError):
    '''Raised when a Parser uses all input without accepting.'''

    def __init__(self, start_symbol):
        message = 'Consumed all input without reducing {}'.format(start_symbol)
        super(StartSymbolNotReducedError, self).__init__(message)
