import typing as t
import pytest


def _run(code: str, *, env: t.Optional[t.Dict[str, object]] = None) -> object:
    import ast
    from baku.minieval import StrictVisitor, ContextForEvaluation

    t = ast.parse(code)
    v = StrictVisitor(ContextForEvaluation(env))
    v.visit(t)
    return v.stack[-1][-1].val


class ob:
    x = 10
    y = 20


@pytest.mark.parametrize(
    "code, env",
    [
        ("1", None),
        # BinOp
        ("1 + 1", None),
        ("2 * 3", None),
        ("2 * (3 + 1)", None),
        ("(2 * 3) + 1", None),
        # Name
        ("x", {"x": 10}),
        ("x + 1", {"x": 10}),
        ("(x + 1) * x", {"x": 10}),
        ("x * 3", {"x": "foo"}),
        # Compare
        ("x > 10", {"x": 10}),
        ("x >= 10", {"x": 10}),
        ("0 < x <= 10", {"x": 10}),
        ("0 < x < 10", {"x": 10}),
        ("10 < x <= 100", {"x": 10}),
        ("0 < x <= 10 < y < 20", {"x": 10, "y": 20}),
        ("0 < x <= 10 < y <= 20", {"x": 10, "y": 20}),
        # BoolOp
        ("True and True", None),
        ("True and False", None),
        ("False or True", None),
        ("False or False", None),
        ("0 < x and x <= 10", {"x": 10}),
        # dict
        ("d['x'] + d['y']", {"d": {"x": 10, "y": 20}}),
        # object
        ("ob.x * ob.y", {"ob": ob}),
        # call
        ("x.center(10)", {"x": "foo"}),
        ("x.split(sep='/')", {"x": "foo/bar/boo"}),
        # tuple, list, dict, set
        ("""(d["x"], d.get("y"))""", {"d": {"x": 10}}),
        ("""[d["x"], d.get("y")]""", {"d": {"x": 10}}),
        ("""{"x": d["x"], "y": d.get("y")}""", {"d": {"x": 10}}),
        ("""{1, x, 3}""", {"x": 10}),
    ],
)
def test_(code, env):
    actual = _run(code, env=env)
    expected = eval(code, {"__builtins__": None}, env)
    assert actual == expected


def test_ng():
    with pytest.raises(NameError):
        _run("__import__", env={"__import__": None})
