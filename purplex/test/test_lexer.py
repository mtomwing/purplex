"""Tests for purplex's lexer."""

from mock import patch

import pytest

import purplex
import purplex.exception


class FooBarLexer(purplex.Lexer):
    FOO = purplex.TokenDef(r'foo')
    BAR = purplex.TokenDef(r'bar')


def test_lex_empty_string():
    tokens = list(FooBarLexer(''))

    assert len(tokens) == 0


def test_lex_foobar():
    tokens = list(FooBarLexer('foobar'))

    assert len(tokens) == 2

    assert tokens[0].name == 'FOO'
    assert tokens[0].value == 'foo'
    assert tokens[0].defn == FooBarLexer.FOO
    assert tokens[0].line_num == 1
    assert tokens[0].line_pos == 1

    assert tokens[1].name == 'BAR'
    assert tokens[1].value == 'bar'
    assert tokens[1].defn == FooBarLexer.BAR
    assert tokens[1].line_num == 1
    assert tokens[1].line_pos == 4


def test_lex_foobar_error():
    tokens = []
    with pytest.raises(purplex.exception.NoMatchingTokenFoundError):
        for token in FooBarLexer('foobarerror'):
            tokens.append(token)

    assert len(tokens) == 2


class LongestLexer(purplex.Lexer):
    DOUBLE_FOO = purplex.TokenDef(r'foofoo')
    FOO = purplex.TokenDef(r'foo')
    TRIPLE_FOO = purplex.TokenDef(r'foofoofoo')


def test_lex_longest_first():
    tokens = list(LongestLexer('foofoofoofoofoo'))
    assert [t.name for t in tokens] == ['TRIPLE_FOO', 'DOUBLE_FOO']


class SubclassedLongestLexer(LongestLexer):
    QUAD_FOO = purplex.TokenDef(r'foofoofoofoo')


def test_lex_subclass_longest_first():
    tokens = list(SubclassedLongestLexer('foofoofoofoofoo'))
    assert [t.name for t in tokens] == ['QUAD_FOO', 'FOO']


class TieLexer_foofirst(purplex.Lexer):
    FOO = purplex.TokenDef(r'foo')
    THREE_LETTERS = purplex.TokenDef(r'...')


class TieLexer_foosecond(purplex.Lexer):
    THREE_LETTERS = purplex.TokenDef(r'...')
    FOO = purplex.TokenDef(r'foo')


def test_lex_tie_in_order():
    tokens = list(TieLexer_foofirst('foo'))
    assert [t.name for t in tokens] == ['FOO']
    tokens = list(TieLexer_foosecond('foo'))
    assert [t.name for t in tokens] == ['THREE_LETTERS']


class CallbackLexer(purplex.Lexer):
    FOO = purplex.TokenDef(r'foo')
    BAR = purplex.TokenDef(r'bar')
    BAZ = purplex.TokenDef(r'baz')

    def on_BAR(self, token):
        pass

    def on_BAZ(self, token):
        pass


@patch.object(CallbackLexer, 'on_BAR')
@patch.object(CallbackLexer, 'on_BAZ')
def test_lex_token_callbacks(on_BAR, on_BAZ):
    list(CallbackLexer('foobar'))
    assert CallbackLexer.on_BAR.called
    assert not CallbackLexer.on_BAZ.called


class IgnoreLexer(purplex.Lexer):
    IDENT = purplex.TokenDef(r'[a-zA-Z]+')
    WHITESPACE = purplex.TokenDef('[\s\n]+', ignore=True)


def test_lex_ignored_token():
    tokens = list(IgnoreLexer('ab    cd'))
    assert len(tokens) == 2
    assert 'WHITESPACE' not in [t.name for t in tokens]


def test_lex_newline_position():
    tokens = list(IgnoreLexer('ab\ncd\n ef'))
    assert len(tokens) == 3

    assert tokens[0].value == 'ab'
    assert tokens[0].line_num == 1
    assert tokens[0].line_pos == 1

    assert tokens[1].value == 'cd'
    assert tokens[1].line_num == 2
    assert tokens[1].line_pos == 1

    assert tokens[2].value == 'ef'
    assert tokens[2].line_num == 3
    assert tokens[2].line_pos == 2
