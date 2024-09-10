"""
parser.py -- implement parser for simple expressions

Accept a string of tokens, return an AST expressed as stack of dictionaries
"""
"""
    simple_expression = number | "(" expression ")" | "-" simple_expression
    factor = simple_expression
    term = factor { "*"|"/" factor }
    expression = term { "+"|"-" term }
"""

from pprint import pprint

from tokenizer import tokenize

def parse_simple_expression(tokens):
    """
    simple_expression = number | "(" expression ")" | "-" simple_expression
    """
    if tokens[0]["tag"] == "number":
        return tokens[0], tokens[1:]
    if tokens[0]["tag"] == "(":
        node, tokens = parse_expression(tokens[1:])
        assert tokens[0]["tag"] == ")", "Error: expected ')'"
        return node, tokens[1:]
    if tokens[0]["tag"] == "-":
        node, tokens = parse_simple_expression(tokens[1:])
        node = {"tag":"negate", "value":node}
        return node, tokens


def parse_expression(tokens):
    return parse_simple_expression(tokens)

def test_parse_simple_expression():
    """
    simple_expression = number | "(" expression ")" | "-" simple_expression
    """
    print("testing parse_simple_expression")
    tokens = tokenize("2")
    ast, tokens = parse_simple_expression(tokens)
    assert ast["tag"] == "number"
    assert ast["value"] == 2
    # pprint(ast)
    tokens = tokenize("(2)")
    ast, tokens = parse_simple_expression(tokens)
    assert ast["tag"] == "number"
    assert ast["value"] == 2
    # pprint(ast)
    tokens = tokenize("-2")
    ast, tokens = parse_simple_expression(tokens)
    assert ast == {
        "tag": "negate",
        "value": {"position": 1, "tag": "number", "value": 2},
    }
    # pprint(ast)
    tokens = tokenize("-(2)")
    ast, tokens = parse_simple_expression(tokens)
    assert ast == {
        "tag": "negate",
        "value": {"position": 2, "tag": "number", "value": 2},
    }
    # pprint(ast)

def parse_factor(tokens):
    """
    factor = simple_expression
    """
    return parse_simple_expression(tokens)

def test_parse_factor():
    """
    factor = simple_expression
    """
    print("testing parse_factor")
    for s in ["2", "(2)", "-2"]:
        assert parse_factor(tokenize(s)) == parse_simple_expression(tokenize(s))


def parse_term(tokens):
    """
    term = factor { "*"|"/" factor }
    """
    node, tokens = parse_factor(tokens)
    while tokens[0]["tag"] in ["*", "/"]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_factor(tokens[1:])
        node = {"tag": tag, "left": node, "right": right_node}
    return node, tokens


def test_parse_term():
    """
    term = factor { "*"|"/" factor }
    """
    tokens = tokenize("2")
    ast, tokens = parse_term(tokens)
    assert ast["tag"] == "number"
    assert ast["value"] == 2
    tokens = tokenize("2*2")
    ast, tokens = parse_term(tokens)
    assert ast == {
        "tag": "*",
        "left": {"tag": "number", "value": 2, "position": 0},
        "right": {"tag": "number", "value": 2, "position": 2},
    }


def parse_expression(tokens):
    """
    expression = term { "+"|"-" term }
    """
    node, tokens = parse_term(tokens)
    while tokens[0]["tag"] in ["+", "-"]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_term(tokens[1:])
        node = {"tag": tag, "left": node, "right": right_node}
    return node, tokens


def test_parse_expression():
    """
    expression = term { "+"|"-" term }
    """
    tokens = tokenize("2")
    ast, tokens = parse_term(tokens)
    assert ast == {"tag": "number", "value": 2, "position": 0}
    ast, tokens = parse_expression(tokenize("2+3"))
    assert ast == {
        "tag": "+",
        "left": {"tag": "number", "value": 2, "position": 0},
        "right": {"tag": "number", "value": 3, "position": 2},
    }
    ast, tokens = parse_expression(tokenize("1+2+3"))
    assert ast == {
        "tag": "+",
        "left": {
            "tag": "+",
            "left": {"tag": "number", "value": 1, "position": 0},
            "right": {"tag": "number", "value": 2, "position": 2},
        },
        "right": {"tag": "number", "value": 3, "position": 4},
    }
    ast, tokens = parse_expression(tokenize("3-2"))
    assert ast == {
        "tag": "-",
        "left": {"tag": "number", "value": 3, "position": 0},
        "right": {"tag": "number", "value": 2, "position": 2},
    }
    ast, tokens = parse_expression(tokenize("1+2*3"))
    assert ast == {
        "tag": "+",
        "left": {"tag": "number", "value": 1, "position": 0},
        "right": {
            "tag": "*",
            "left": {"tag": "number", "value": 2, "position": 2},
            "right": {"tag": "number", "value": 3, "position": 4},
        },
    }
    ast, tokens = parse_expression(tokenize("(1+2)*3"))
    assert ast == {
        "tag": "*",
        "left": {
            "tag": "+",
            "left": {"tag": "number", "value": 1, "position": 1},
            "right": {"tag": "number", "value": 2, "position": 3},
        },
        "right": {"tag": "number", "value": 3, "position": 6},
    }
    ast, tokens = parse_expression(tokenize("-(1+2)*-3"))
    assert ast == {
        "tag": "*",
        "left": {
            "tag": "negate",
            "value": {
                "tag": "+",
                "left": {"tag": "number", "value": 1, "position": 2},
                "right": {"tag": "number", "value": 2, "position": 4},
            },
        },
        "right": {
            "tag": "negate",
            "value": {"tag": "number", "value": 3, "position": 8},
        },
    }


if __name__ == "__main__":
    test_parse_simple_expression()
    test_parse_factor()
    print("done")