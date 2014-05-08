import pytest

from purplex.exception import TokenMatchesEmptyStringError
from purplex.token import TokenDef, Token


def test_token_definition():
    TokenDef(r'a+b*')

    with pytest.raises(TokenMatchesEmptyStringError):
        TokenDef(r'a*b*')


@pytest.mark.parametrize('name,value,defn,line_num,line_pos', [
    ('LPAREN', '{', TokenDef(r'{'), 0, 0),
    ('RPAREN', '}', TokenDef(r'}'), 100, 0),
])
def test_token(name, value, defn, line_num, line_pos):
    token = Token(name, value, defn, line_num, line_pos)
    assert token.name == name
    assert token.value == value
    assert token.defn == defn
    assert token.line_num == line_num
    assert token.line_pos == line_pos
    assert str(token) != ''
    assert len(token) == len(value)
