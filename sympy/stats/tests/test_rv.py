from __future__ import unicode_literals
from sympy import (
    S,
    Symbol,
    Interval,
    exp,
    symbols,
    Eq,
    cos,
    And,
    Tuple,
    integrate,
    oo,
    sin,
    Sum,
    Basic,
    DiracDelta,
    Lambda,
    log,
    pi,
    FallingFactorial,
    Rational,
)
from sympy.stats import (
    Die,
    Normal,
    Exponential,
    FiniteRV,
    P,
    E,
    H,
    variance,
    density,
    given,
    independent,
    dependent,
    where,
    pspace,
    random_symbols,
    sample,
    Geometric,
    factorial_moment,
    Binomial,
    Hypergeometric,
    DiscreteUniform,
    Poisson,
    characteristic_function,
    moment_generating_function,
)
from sympy.stats.rv import (
    IndependentProductPSpace,
    rs_swap,
    Density,
    NamedArgsMixin,
    RandomSymbol,
    sample_iter,
    PSpace,
)
from sympy.testing.pytest import raises
from sympy.core.numbers import comp
from sympy.stats.frv_types import BernoulliDistribution


def test_where():
    X, Y = Die("X"), Die("Y")
    Z = Normal("Z", 0, 1)

    assert where(Z ** 2 <= 1).set == Interval(-1, 1)
    assert where(Z ** 2 <= 1).as_boolean() == Interval(-1, 1).as_relational(Z.symbol)
    assert where(And(X > Y, Y > 4)).as_boolean() == And(
        Eq(X.symbol, 6), Eq(Y.symbol, 5)
    )

    assert len(where(X < 3).set) == 2
    assert 1 in where(X < 3).set

    X, Y = Normal("X", 0, 1), Normal("Y", 0, 1)
    assert where(And(X ** 2 <= 1, X >= 0)).set == Interval(0, 1)
    XX = given(X, And(X ** 2 <= 1, X >= 0))
    assert XX.pspace.domain.set == Interval(0, 1)
    assert XX.pspace.domain.as_boolean() == And(
        0 <= X.symbol, X.symbol ** 2 <= 1, -oo < X.symbol, X.symbol < oo
    )

    with raises(TypeError):
        XX = given(X, X + 3)


def test_random_symbols():
    X, Y = Normal("X", 0, 1), Normal("Y", 0, 1)

    assert set(random_symbols(2 * X + 1)) == set((X,))
    assert set(random_symbols(2 * X + Y)) == set((X, Y))
    assert set(random_symbols(2 * X + Y.symbol)) == set((X,))
    assert set(random_symbols(2)) == set()


def test_characteristic_function():
    #  Imports I from sympy
    from sympy import I

    X = Normal("X", 0, 1)
    Y = DiscreteUniform("Y", [1, 2, 7])
    Z = Poisson("Z", 2)
    t = symbols("_t")
    P = Lambda(t, exp(-(t ** 2) / 2))
    Q = Lambda(t, exp(7 * t * I) / 3 + exp(2 * t * I) / 3 + exp(t * I) / 3)
    R = Lambda(t, exp(2 * exp(t * I) - 2))

    assert characteristic_function(X) == P
    assert characteristic_function(Y) == Q
    assert characteristic_function(Z) == R


def test_moment_generating_function():

    X = Normal("X", 0, 1)
    Y = DiscreteUniform("Y", [1, 2, 7])
    Z = Poisson("Z", 2)
    t = symbols("_t")
    P = Lambda(t, exp(t ** 2 / 2))
    Q = Lambda(t, (exp(7 * t) / 3 + exp(2 * t) / 3 + exp(t) / 3))
    R = Lambda(t, exp(2 * exp(t) - 2))

    assert moment_generating_function(X) == P
    assert moment_generating_function(Y) == Q
    assert moment_generating_function(Z) == R


def test_sample_iter():

    X = Normal("X", 0, 1)
    Y = DiscreteUniform("Y", [1, 2, 7])
    Z = Poisson("Z", 2)

    expr = X ** 2 + 3
    iterator = sample_iter(expr)

    expr2 = Y ** 2 + 5 * Y + 4
    iterator2 = sample_iter(expr2)

    expr3 = Z ** 3 + 4
    iterator3 = sample_iter(expr3)

    def is_iterator(obj):
        if (
            hasattr(obj, "__iter__")
            and (hasattr(obj, "next") or hasattr(obj, "__next__"))
            and callable(obj.__iter__)
            and obj.__iter__() is obj
        ):
            return True
        else:
            return False

    assert is_iterator(iterator)
    assert is_iterator(iterator2)
    assert is_iterator(iterator3)


def test_pspace():
    X, Y = Normal("X", 0, 1), Normal("Y", 0, 1)
    x = Symbol("x")

    raises(ValueError, lambda: pspace(5 + 3))
    raises(ValueError, lambda: pspace(x < 1))
    assert pspace(X) == X.pspace
    assert pspace(2 * X + 1) == X.pspace
    assert pspace(2 * X + Y) == IndependentProductPSpace(Y.pspace, X.pspace)


def test_rs_swap():
    X = Normal("x", 0, 1)
    Y = Exponential("y", 1)

    XX = Normal("x", 0, 2)
    YY = Normal("y", 0, 3)

    expr = 2 * X + Y
    assert expr.subs(rs_swap((X, Y), (YY, XX))) == 2 * XX + YY


def test_RandomSymbol():

    X = Normal("x", 0, 1)
    Y = Normal("x", 0, 2)
    assert X.symbol == Y.symbol
    assert X != Y

    assert X.name == X.symbol.name

    X = Normal("lambda", 0, 1)  # make sure we can use protected terms
    X = Normal("Lambda", 0, 1)  # make sure we can use SymPy terms


def test_RandomSymbol_diff():
    X = Normal("x", 0, 1)
    assert (2 * X).diff(X)


def test_random_symbol_no_pspace():
    x = RandomSymbol(Symbol("x"))
    assert x.pspace == PSpace()


def test_overlap():
    X = Normal("x", 0, 1)
    Y = Normal("x", 0, 2)

    raises(ValueError, lambda: P(X > Y))


def test_IndependentProductPSpace():
    X = Normal("X", 0, 1)
    Y = Normal("Y", 0, 1)
    px = X.pspace
    py = Y.pspace
    assert pspace(X + Y) == IndependentProductPSpace(px, py)
    assert pspace(X + Y) == IndependentProductPSpace(py, px)


def test_E():
    assert E(5) == 5


def test_H():
    X = Normal("X", 0, 1)
    D = Die("D", sides=4)
    G = Geometric("G", 0.5)
    assert H(X, X > 0) == -log(2) / 2 + S.Half + log(pi) / 2
    assert H(D, D > 2) == log(2)
    assert comp(H(G).evalf().round(2), 1.39)


def test_Sample():
    X = Die("X", 6)
    Y = Normal("Y", 0, 1)
    z = Symbol("z")

    assert sample(X) in [1, 2, 3, 4, 5, 6]
    assert sample(X + Y).is_Float

    P(X + Y > 0, Y < 0, numsamples=10).is_number
    assert E(X + Y, numsamples=10).is_number
    assert variance(X + Y, numsamples=10).is_number

    raises(ValueError, lambda: P(Y > z, numsamples=5))

    assert P(sin(Y) <= 1, numsamples=10) == 1
    assert P(sin(Y) <= 1, cos(Y) < 1, numsamples=10) == 1

    # Make sure this doesn't raise an error
    E(Sum(1 / z ** Y, (z, 1, oo)), Y > 2, numsamples=3)

    assert all(i in range(1, 7) for i in density(X, numsamples=10))
    assert all(i in range(4, 7) for i in density(X, X > 3, numsamples=10))


def test_given():
    X = Normal("X", 0, 1)
    Y = Normal("Y", 0, 1)
    A = given(X, True)
    B = given(X, Y > 2)

    assert X == A == B


def test_factorial_moment():
    X = Poisson("X", 2)
    Y = Binomial("Y", 2, S.Half)
    Z = Hypergeometric("Z", 4, 2, 2)
    assert factorial_moment(X, 2) == 4
    assert factorial_moment(Y, 2) == S.Half
    assert factorial_moment(Z, 2) == Rational(1, 3)

    x, y, z, l = symbols("x y z l")
    Y = Binomial("Y", 2, y)
    Z = Hypergeometric("Z", 10, 2, 3)
    assert factorial_moment(Y, l) == y ** 2 * FallingFactorial(2, l) + 2 * y * (
        1 - y
    ) * FallingFactorial(1, l) + (1 - y) ** 2 * FallingFactorial(0, l)
    assert (
        factorial_moment(Z, l)
        == 7 * FallingFactorial(0, l) / 15
        + 7 * FallingFactorial(1, l) / 15
        + FallingFactorial(2, l) / 15
    )


def test_dependence():
    X, Y = Die("X"), Die("Y")
    assert independent(X, 2 * Y)
    assert not dependent(X, 2 * Y)

    X, Y = Normal("X", 0, 1), Normal("Y", 0, 1)
    assert independent(X, Y)
    assert dependent(X, 2 * X)

    # Create a dependency
    XX, YY = given(Tuple(X, Y), Eq(X + Y, 3))
    assert dependent(XX, YY)


def test_dependent_finite():
    X, Y = Die("X"), Die("Y")
    # Dependence testing requires symbolic conditions which currently break
    # finite random variables
    assert dependent(X, Y + X)

    XX, YY = given(Tuple(X, Y), X + Y > 5)  # Create a dependency
    assert dependent(XX, YY)


def test_normality():
    X, Y = Normal("X", 0, 1), Normal("Y", 0, 1)
    x = Symbol("x", real=True, finite=True)
    z = Symbol("z", real=True, finite=True)
    dens = density(X - Y, Eq(X + Y, z))

    assert integrate(dens(x), (x, -oo, oo)) == 1


def test_Density():
    X = Die("X", 6)
    d = Density(X)
    assert d.doit() == density(X)


def test_NamedArgsMixin():
    class Foo(Basic, NamedArgsMixin):
        _argnames = "foo", "bar"

    a = Foo(1, 2)

    assert a.foo == 1
    assert a.bar == 2

    raises(AttributeError, lambda: a.baz)

    class Bar(Basic, NamedArgsMixin):
        pass

    raises(AttributeError, lambda: Bar(1, 2).foo)


def test_density_constant():
    assert density(3)(2) == 0
    assert density(3)(3) == DiracDelta(0)


def test_real():
    x = Normal("x", 0, 1)
    assert x.is_real


def test_issue_10052():
    X = Exponential("X", 3)
    assert P(X < oo) == 1
    assert P(X > oo) == 0
    assert P(X < 2, X > oo) == 0
    assert P(X < oo, X > oo) == 0
    assert P(X < oo, X > 2) == 1
    assert P(X < 3, X == 2) == 0
    raises(ValueError, lambda: P(1))
    raises(ValueError, lambda: P(X < 1, 2))


def test_issue_11934():
    density = {0: 0.5, 1: 0.5}
    X = FiniteRV("X", density)
    assert E(X) == 0.5
    assert P(X >= 2) == 0


def test_issue_8129():
    X = Exponential("X", 4)
    assert P(X >= X) == 1
    assert P(X > X) == 0
    assert P(X > X + 1) == 0


def test_issue_12237():
    X = Normal("X", 0, 1)
    Y = Normal("Y", 0, 1)
    U = P(X > 0, X)
    V = P(Y < 0, X)
    W = P(X + Y > 0, X)
    assert W == P(X + Y > 0, X)
    assert U == BernoulliDistribution(S.Half, S.Zero, S.One)
    assert V == S.Half
