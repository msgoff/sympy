#!/usr/bin/env python

"""Substitution example

Demonstrates substitution.
"""

import sympy
from sympy import pprint


def main():
    x = sympy.Symbol("x")
    y = sympy.Symbol("y")

    e = 1 / sympy.cos(x)
    print()
    pprint(e)
    print("\n")
    pprint(e.subs(sympy.cos(x), y))
    print("\n")
    pprint(e.subs(sympy.cos(x), y).subs(y, x ** 2))

    e = 1 / sympy.log(x)
    e = e.subs(x, sympy.Float("2.71828"))
    print("\n")
    pprint(e)
    print("\n")
    pprint(e.evalf())
    print()

    a = sympy.Symbol("a")
    b = sympy.Symbol("b")
    e = a * 2 + a ** b / a
    print("\n")
    pprint(e)
    a = 2
    print("\n")
    pprint(e.subs(a, 8))
    print()


if __name__ == "__main__":
    main()
