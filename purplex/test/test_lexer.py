"""Tests for purplex's lexer."""

import pytest

import purplex


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
    assert tokens[0].defn == FooBarLexer.tokens['FOO']
    assert tokens[0].line_num == 1
    assert tokens[0].line_pos == 1

    assert tokens[1].name == 'BAR'
    assert tokens[1].value == 'bar'
    assert tokens[1].defn == FooBarLexer.tokens['BAR']
    assert tokens[1].line_num == 1
    assert tokens[1].line_pos == 4


def test_lex_foobar_error():
    tokens = []
    with pytest.raises(Exception) as e:
        for token in FooBarLexer('foobarerror'):
            tokens.append(token)

    assert len(tokens) == 2
    assert e.exconly() == 'Exception: No token definition matched: "e"'


class LongestLexer(purplex.Lexer):
    DOUBLE_FOO = purplex.TokenDef(r'foofoo')
    FOO = purplex.TokenDef(r'foo')
    TRIPLE_FOO = purplex.TokenDef(r'foofoofoo')


def test_lex_longest_first():
    tokens = list(LongestLexer('foofoofoofoofoo'))
    assert [t.name for t in tokens] == ['TRIPLE_FOO', 'DOUBLE_FOO']


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
