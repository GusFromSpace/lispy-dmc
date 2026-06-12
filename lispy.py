#!/usr/bin/env python3
"""lispy.py -- a tiny Scheme interpreter.

Adapted from Peter Norvig's "(How to Write a (Lisp) Interpreter (in Python)))"
(http://norvig.com/lispy.html), which is in the public domain. This is the
reference source for the demoniC translation in ``lispy.dmc``; both evaluate the
same Scheme programs and print identical output.

Pipeline: tokenizer -> recursive-descent parser -> tree-walking evaluator over
a tagged AST (numbers, symbols, and lists), with an environment mapping symbols
to values.
"""

from functools import reduce


# -- Tokenizer --------------------------------------------------------------
# "(+ 1 2)" -> ["(", "+", "1", "2", ")"]
def tokenize(src):
    return src.replace("(", " ( ").replace(")", " ) ").split()


# -- Atom: a token becomes a number or a symbol -----------------------------
def atom(tok):
    try:
        return int(tok)
    except ValueError:
        try:
            return float(tok)
        except ValueError:
            return tok  # a symbol


# -- Parser -----------------------------------------------------------------
# Recursive descent over the token list. Returns (node, next_index).
# A node is an int/float, a str symbol, or a list of nodes.
def parse_from(toks, start):
    tok = toks[start]
    if tok == "(":
        node = []
        i = start + 1
        while i < len(toks):
            if toks[i] == ")":
                return node, i + 1
            child, i = parse_from(toks, i)
            node.append(child)
        raise SyntaxError("unexpected EOF: missing )")
    elif tok == ")":
        raise SyntaxError("unexpected )")
    else:
        return atom(tok), start + 1


def parse(src):
    node, _ = parse_from(tokenize(src), 0)
    return node


# -- Evaluator --------------------------------------------------------------
# env maps symbol -> number. Returns the numeric value of an expression node.
def eval_node(node, env):
    if isinstance(node, str):           # symbol
        return env[node]
    if not isinstance(node, list):      # number
        return node

    op = node[0]
    if op == "if":                      # (if test conseq alt)
        _, test, conseq, alt = node
        branch = conseq if eval_node(test, env) != 0 else alt
        return eval_node(branch, env)

    args = [eval_node(arg, env) for arg in node[1:]]
    if op == "+":
        return sum(args)
    if op == "*":
        return reduce(lambda a, b: a * b, args, 1)
    if op == "-":
        if len(args) == 1:
            return -args[0]
        return reduce(lambda a, b: a - b, args)
    if op == "<":
        return 1 if args[0] < args[1] else 0

    raise SyntaxError("unknown operator: " + str(op))


def run(src, env=None):
    return eval_node(parse(src), {} if env is None else env)


def main():
    print(run("(+ 1 (* 2 3))"))         # 7
    print(run("(if (< 2 3) 10 20)"))    # 10
    print(run("(- 10 1 2 3)"))          # 4
    print(run("(* (+ 1 2) (- 8 3))"))   # 15


if __name__ == "__main__":
    main()
