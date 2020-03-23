import pytest
from functools import partial


@pytest.fixture(scope="module")
def q():
    from baku.q import q, QBuilder

    return partial(q, builder=QBuilder())


def test_simple(q):
    assert str(q("x")) == "x"


def test_and(q):
    assert str(q("x").And(q("y"))) == "(x and y)"


def test_with_literal(q):
    assert str(q("x").endswith("oo")) == "x.endswith('oo')"


def test_lt(q):
    assert str(q(10).Lt(q("x"))) == "(10 < x)"


def test_lt2(q):
    # TODO: 10 < x < 100
    assert str(q(10).Lt(q("x")).Lt(100)) == "((10 < x) < 100)"


def test_attr(q):
    assert str(q("x").foo.bar(q("z"), "xxx").boo()) == "x.foo.bar(z, 'xxx').boo()"


def test_items(q):
    assert (
        str(q("d")["gender"].In(["male", "female", "not-known"]))
        == "(d['gender'] in ['male', 'female', 'not-known'])"
    )


def test_complex(q):
    assert (
        str(q("x").Add("y").neg().add(q("int")(True))) == "(- (x + y)).add(int(True))"
    )
