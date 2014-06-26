from purplex.grammar import Grammar, Production, END_OF_INPUT


def test_grammar_mostly():
    noop = lambda args: args
    grammar = Grammar(['+', '*', '(', ')', 'id'], [
        Production("E : T E'", noop),
        Production("E' : + T E'", noop),
        Production("E' : <empty>", noop),
        Production("T : F T'", noop),
        Production("T' : * F T'", noop),
        Production("T' : <empty>", noop),
        Production("F : ( E )", noop),
        Production("F : id", noop),
    ], start="E")

    assert grammar._first == {
        # Non-terminals
        grammar.start_symbol: set(["(", "id"]),
        "E": set(["(", "id"]),
        "E'": set(["<empty>", "+"]),
        "T": set(["(", "id"]),
        "T'": set(["<empty>", "*"]),
        "F": set(["(", "id"]),

        # Terminals
        "+": set(["+"]),
        "*": set(["*"]),
        "(": set(["("]),
        ")": set([")"]),
        "id": set(["id"]),
        END_OF_INPUT: set([END_OF_INPUT]),
    }
    assert grammar._follow == {
        grammar.start_symbol: set([END_OF_INPUT]),
        "E": set([')', END_OF_INPUT]),
        "E'": set([')', END_OF_INPUT]),
        "T": set([')', '+', END_OF_INPUT]),
        "T'": set([')', '+', END_OF_INPUT]),
        "F": set([')', '+', '*', END_OF_INPUT]),
    }


def test_grammar_epsilon():
    noop = lambda args: args
    grammar = Grammar(['id'], [
        Production('A : B', noop),
        Production('B : C', noop),
        Production('C : <empty>', noop),
    ], start='A')

    assert grammar._first == {
        grammar.start_symbol: set(['<empty>']),
        'A': set(['<empty>']),
        'B': set(['<empty>']),
        'C': set(['<empty>']),

        'id': set(['id']),
        END_OF_INPUT: set([END_OF_INPUT]),
    }
    assert grammar._follow == {
        grammar.start_symbol: set([END_OF_INPUT]),
        'A': set([END_OF_INPUT]),
        'B': set([END_OF_INPUT]),
        'C': set([END_OF_INPUT]),
    }
