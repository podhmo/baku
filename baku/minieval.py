import typing as t
import ast
from functools import partial
import logging
from baku.q import QEvaluator, QBuilder, q, Q, QArgs

logger = logging.getLogger(__name__)


class StrictVisitor(ast.NodeVisitor):
    def __init__(self, ctx) -> None:
        self.stack = [[]]
        self.ctx = ctx

    # override
    def generic_visit(self, node: ast.AST):
        method = "visit_" + node.__class__.__name__
        raise NotImplementedError(method)

    def visit_Module(self, node: ast.Module):
        logger.debug("trace Module depth=%d %s", len(self.stack), node)
        assert len(node.body) == 1, "must be expr, len(node) == 1"
        self.visit(node.body[0])

    def visit_Expr(self, node: ast.Expr):
        logger.debug("trace Expr depth=%d %s", len(self.stack), node)
        self.visit(node.value)

    def visit_Name(self, node: ast.Name):
        logger.debug("trace Name depth=%d %s", len(self.stack), node)
        self.stack[-1].append(self.ctx.Name(node.id))

    def visit_Constant(self, node: ast.Constant):
        logger.debug("trace Constant depth=%d %s", len(self.stack), node)
        self.stack[-1].append(self.ctx.Value(ast.literal_eval(node)))

    def visit_BinOp(self, node: ast.BinOp):
        logger.debug(
            "trace BinOp depth=%d %s, %s, %s",
            len(self.stack),
            node,
            node.left,
            node.right,
        )
        self.stack.append([])
        self.visit(node.left)
        self.visit(node.right)
        left, right = self.stack.pop()

        method = getattr(left, node.op.__class__.__name__)
        self.stack[-1].append(method(right))

    def visit_BoolOp(self, node: ast.BoolOp):
        # short circuit?
        logger.debug(
            "trace BoolOp depth=%d %s, %s, %s",
            len(self.stack),
            node,
            node.op,
            node.values,
        )
        self.stack.append([])
        self.visit(node.values[0])
        l_value = self.stack[-1].pop()

        for v in node.values[1:]:
            self.visit(v)
            method = getattr(l_value, node.op.__class__.__name__)
            r_value = self.stack[-1].pop()
            l_value = method(r_value)

        assert not self.stack.pop()  # empty list
        self.stack[-1].append(l_value)

    def visit_Compare(self, node: ast.Compare):
        # short circuit?
        logger.debug(
            "trace Compare depth=%d %s, %s, %s",
            len(self.stack),
            node,
            node.ops,
            node.comparators,
        )
        self.stack.append([])
        self.visit(node.left)
        l_val = self.stack[-1].pop()

        assert len(node.ops) == len(node.comparators)
        acc = None
        for i, (op, right) in enumerate(zip(node.ops, node.comparators)):
            self.visit(right)
            r_val = self.stack[-1].pop()
            method = getattr(l_val, op.__class__.__name__)
            if acc is None:
                acc = method(r_val)
            else:
                acc = acc.And(method(r_val))
            l_val = r_val

        assert not self.stack.pop()  # empty list
        self.stack[-1].append(acc)

    def visit_Subscript(self, node: ast.Subscript):
        logger.debug(
            "trace Subscript depth=%d %s, %s, %s",
            len(self.stack),
            node,
            node.value,
            node.slice,
        )

        # e.g. d["x"]
        self.stack.append([])
        self.visit(node.value)
        c = self.stack[-1].pop()
        self.visit(node.slice.value)
        k = self.stack[-1].pop()

        assert not self.stack.pop()
        self.stack[-1].append(c[k])

    def visit_Attribute(self, node: ast.Attribute):
        logger.debug(
            "trace Attribute depth=%d %s, %s, %s",
            len(self.stack),
            node,
            node.value,
            node.attr,
        )

        # e.g. ob.x
        self.stack.append([])
        self.visit(node.value)
        ob = self.stack[-1].pop()

        assert not self.stack.pop()
        self.stack[-1].append(getattr(ob, node.attr))

    def visit_Call(self, node: ast.Call):
        logger.debug(
            "trace Call depth=%d %s, %s, %s, %s",
            len(self.stack),
            node,
            node.func,
            node.args,
            node.keywords,
        )

        self.stack.append([])
        self.visit(node.func)
        fn = self.stack[-1].pop()

        for x in node.args:
            self.visit(x)
        args = self.stack.pop()

        self.stack.append([])
        for keyword in node.keywords:
            # keyword
            self.visit(keyword.value)
            v = self.stack[-1].pop()
            self.stack[-1].append((keyword.arg, v))
        kwargs = dict(self.stack.pop())

        self.stack[-1].append(fn(*args, **kwargs))

    def visit_Tuple(self, node: ast.Tuple):
        logger.debug(
            "trace Tuple depth=%d %s, %s", len(self.stack), node, node.elts,
        )

        self.stack.append([])

        for x in node.elts:
            self.visit(x)
        xs = self.stack.pop()
        self.stack[-1].append(self.ctx.Tuple(xs))

    def visit_List(self, node: ast.List):
        logger.debug(
            "trace List depth=%d %s, %s", len(self.stack), node, node.elts,
        )

        self.stack.append([])

        for x in node.elts:
            self.visit(x)
        xs = self.stack.pop()
        self.stack[-1].append(self.ctx.List(xs))

    def visit_Set(self, node: ast.Set):
        logger.debug(
            "trace Set depth=%d %s, %s", len(self.stack), node, node.elts,
        )

        self.stack.append([])

        for x in node.elts:
            self.visit(x)
        xs = self.stack.pop()
        self.stack[-1].append(self.ctx.Set(xs))

    def visit_Dict(self, node: ast.Dict):
        logger.debug(
            "trace Dict depth=%d %s, %s, %s",
            len(self.stack),
            node,
            node.keys,
            node.values,
        )

        self.stack.append([])
        for k in node.keys:
            self.visit(k)
        ks = self.stack.pop()

        self.stack.append([])
        for v in node.values:
            self.visit(v)
        vs = self.stack.pop()

        self.stack[-1].append(self.ctx.Dict(ks, vs))


class ContextForBuilding:
    def __init__(self, env: t.Dict[str, object]) -> None:
        self.env = env
        self.builder = QBuilder()

    def Name(self, name: str) -> Q:
        return q(name, builder=self.builder)

    def Value(self, value: object) -> Q:
        return q(repr(value), builder=self.builder)

    def Tuple(self, xs) -> Q:
        return q("({args})", args=QArgs(self.builder, xs, {}))

    def List(self, xs) -> Q:
        return q("[{args}]", args=QArgs(self.builder, xs, {}))

    def Set(self, xs) -> Q:
        return q("{{{args}}}", args=QArgs(self.builder, xs, {}))

    def Dict(self, ks, vs) -> Q:
        return q(
            "{{{args}}}", args=QArgs(self.builder, [], dict(zip(ks, vs)), sep=": ")
        )


class ContextForEvaluation:
    def __init__(self, env: t.Dict[str, object]) -> None:
        self.env = env
        self.builder = QEvaluator()

    def Name(self, name: str) -> Q:
        if name.startswith("_"):
            raise NameError(f"{name!r} is not defined (?)")
        return q(self.env[name], builder=self.builder)

    def Value(self, value: object) -> Q:
        return q(value, builder=self.builder)

    def Tuple(self, xs) -> Q:
        return q(tuple(getattr(x, "val", x) for x in xs))

    def List(self, xs) -> Q:
        return q([getattr(x, "val", x) for x in xs])

    def Set(self, xs) -> Q:
        return q(set(getattr(x, "val", x) for x in xs))

    def Dict(self, ks, vs) -> Q:
        return q({getattr(k, "val", k): getattr(v, "val", v) for k, v in zip(ks, vs)})


def literal_eval_plus(
    code: str,
    *,
    env: t.Optional[t.Dict[str, object]] = None,
    create_ctx=ContextForEvaluation,
) -> object:
    t = ast.parse(code)
    v = StrictVisitor(create_ctx(env))
    v.visit(t)
    return v.stack[-1][-1].val


# TODO: remove
if __name__ == "__main__":

    def run(code: str, *, create_ctx, env=None):
        print(f"env   : {env}")
        print(f"input : {code}")
        t = ast.parse(code)
        v = StrictVisitor(create_ctx(env))
        v.visit(t)
        print(f"output: {v.stack[-1][-1]}")

    def do_all(_run):
        _run("1")
        # BinOp
        _run("1 + 1")
        _run("2 * 3")
        _run("2 * (3 + 1)")
        _run("(2 * 3) + 1")
        # Name
        _run("x", env={"x": 10})
        _run("x + 1", env={"x": 10})
        _run("(x + 1) * x", env={"x": 10})
        _run("x * 3", env={"x": "foo"})
        # Compare
        _run("x > 10", env={"x": 10})
        _run("x >= 10", env={"x": 10})
        _run("0 < x <= 10", env={"x": 10})
        _run("0 < x < 10", env={"x": 10})
        _run("10 < x <= 100", env={"x": 10})
        _run("0 < x <= 10 < y < 20", env={"x": 10, "y": 20})
        _run("0 < x <= 10 < y <= 20", env={"x": 10, "y": 20})
        # BoolOp
        _run("True and True")
        _run("True and False")
        _run("False or True")
        _run("False or False")
        _run("0 < x and x <= 10", env={"x": 10})
        # dict
        _run("d['x'] + d['y']", env={"d": {"x": 10, "y": 20}})
        # object
        class ob:
            x = 10
            y = 20

        _run("ob.x * ob.y", env={"ob": ob})

        # call
        _run("x.center(10)", env={"x": "foo"})
        _run("x.split(sep='/')", env={"x": "foo/bar/boo"})

        # tuple, list, dict, set
        _run("""(d["x"], d.get("y"))""", env={"d": {"x": 10}})
        _run("""[d["x"], d.get("y")]""", env={"d": {"x": 10}})
        _run("""{"x": d["x"], "y": d.get("y")}""", env={"d": {"x": 10}})
        _run("""{1, x, 3}""", env={"x": 10})

    do_all(partial(run, create_ctx=ContextForBuilding))
    print("")
    print("****")
    print("")
    do_all(partial(run, create_ctx=ContextForEvaluation))
