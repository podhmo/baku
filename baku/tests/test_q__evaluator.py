# type: ignore
import pytest
from functools import partial


@pytest.fixture(scope="module")
def q():
    from baku.q import q, QEvaluator

    return partial(q, builder=QEvaluator())


def _run(q):
    return q.builder.build(q)  # TODO: rename method


def test_expr(q):
    assert _run(q(10).Add(20).Mult(2)) == (10 + 20) * 2


def test_method(q):
    assert _run(q("foo").endswith("oo").Is(True)) is True
    assert _run(q("foo").endswith("@@").Is(False)) is True


def test_attr(q):
    class ob:
        class x:
            y = 10

    assert _run(q(ob).x.y) == 10


def test_item(q):
    d = {"x": {"y": 10}}
    assert _run(q(d)["x"]["y"]) == 10


def test_or(q):
    d = {"x": 10}

    lhs = q(d)["x"].In(q([1, 2, 3]))
    assert _run(lhs) is False
    rhs = q(d)["x"].In(q([10]))
    assert _run(rhs) is True

    assert _run(lhs.Or(rhs)) is True
