from __future__ import annotations
import typing as t
import typing_extensions as tx
import operator

# FIXME: val attribute is reserved in internal code


class Q:
    __slots__ = ("builder", "val", "kwargs")

    def __init__(
        self,
        builder: BuilderProtocol,
        val: object,
        kwargs: t.Optional[t.Dict[str, object]],
    ) -> None:
        self.builder = builder
        self.val = val
        self.kwargs = kwargs

    def __call__(self, *args: object, **kwargs: object) -> Q:
        return self.builder.call(self, args, kwargs)

    # name from ast modules's node class name

    def And(self, right: Q) -> Q:
        return self.builder.bop(self, "and", right)

    def Or(self, right: Q) -> Q:
        return self.builder.bop(self, "or", right)

    def Gt(self, right: Q) -> Q:
        return self.builder.bop(self, ">", right)

    def GtE(self, right: Q) -> Q:
        return self.builder.bop(self, ">=", right)

    def Lt(self, right: Q) -> Q:
        return self.builder.bop(self, "<", right)

    def LtE(self, right: Q) -> Q:
        return self.builder.bop(self, "<=", right)

    def Eq(self, right: Q) -> Q:
        return self.builder.bop(self, "==", right)

    def NotEq(self, right: Q) -> Q:
        return self.builder.bop(self, "!=", right)

    def Not(self) -> Q:
        return self.builder.uop(self, "not")

    def Is(self, right: Q) -> Q:
        return self.builder.bop(self, "is", right)

    def IsNot(self, right: Q) -> Q:
        return self.builder.bop(self, "is not", right)

    def In(self, right: Q) -> Q:
        return self.builder.bop(self, "in", right)

    def NotIn(self, right: Q) -> Q:
        return self.builder.bop(self, "not in", right)

    #
    def Add(self, right: Q) -> Q:
        return self.builder.bop(self, "+", right)

    def Sub(self, right: Q) -> Q:
        return self.builder.bop(self, "-", right)

    def Mult(self, right: Q) -> Q:
        return self.builder.bop(self, "*", right)

    def Div(self, right: Q) -> Q:
        return self.builder.bop(self, "/", right)

    def neg(self) -> Q:
        return self.builder.uop(self, "-")

    #
    def __str__(self) -> str:
        return str(self.builder.build(self))

    def __to_string__(self, builder: BuilderProtocol) -> str:
        if not self.kwargs:
            return str(self.val)
        kwargs = {
            k: (v.__to_string__(builder) if hasattr(v, "__to_string__") else v)  # type: ignore
            for k, v in self.kwargs.items()
        }
        return self.val.format(**kwargs)  # type: ignore

    def __getattr__(self, name: str) -> Q:
        if name.startswith("_"):
            raise AttributeError(name)
        return self.builder.getattr(self, name)

    def __getitem__(self, name: str) -> Q:
        return self.builder.getindex(self, name)


class QArgs:
    __slots__ = ("builder", "args", "kwargs", "sep")

    def __init__(
        self,
        builder: BuilderProtocol,
        args: t.Sequence[object],
        kwargs: t.Dict[str, object],
        *,
        sep: str = "="
    ) -> None:
        self.builder = builder
        self.args = args
        self.kwargs = kwargs
        self.sep = sep

    def __to_string__(self, builder: BuilderProtocol) -> str:
        new_args = [
            (
                x.__to_string__(builder)  # type:ignore
                if hasattr(x, "__to_string__")
                else repr(x)
            )
            for x in self.args
        ]
        new_kwargs = [
            "{}{}{}".format(
                k,
                self.sep,
                (
                    x.__to_string__(builder)  # type:ignore
                    if hasattr(x, "__to_string__")
                    else repr(x)
                ),
            )
            for k, x in self.kwargs.items()
        ]
        r = []
        if new_args:
            r.extend(new_args)
        if new_kwargs:
            r.extend(new_kwargs)
        return ", ".join(r)


class BuilderProtocol(tx.Protocol):
    def uop(self, q: Q, name: str) -> Q:
        ...

    def bop(self, q: Q, name: str, right: Q) -> Q:
        ...

    def getattr(self, q: Q, name: str) -> Q:
        ...

    def getindex(self, q: Q, name: str) -> Q:
        ...

    def call(self, q: Q, args: t.Sequence[object], kwargs: t.Dict[str, object]) -> Q:
        ...

    def build(self, q: Q) -> t.Any:
        ...


class QBuilder(BuilderProtocol):
    uop_mapping: t.ClassVar[t.Dict[str, str]] = {}
    bop_mapping: t.ClassVar[t.Dict[str, str]] = {}

    def uop(self, q: Q, name: str) -> Q:
        fmt = "({op} {value})"
        name = self.uop_mapping.get(name, name)
        return q.__class__(self, fmt, kwargs=dict(op=name, value=q))

    def bop(self, q: Q, name: str, right: Q) -> Q:
        fmt = "({left} {op} {right})"
        name = self.bop_mapping.get(name, name)
        return q.__class__(self, fmt, kwargs=dict(op=name, left=q, right=right))

    def getattr(self, q: Q, name: str) -> Q:
        fmt = "{inner}.{name}"
        return q.__class__(self, fmt, kwargs=dict(inner=q, name=name))

    def getindex(self, q: Q, name: str) -> Q:
        name = name if hasattr(name, "builder") else repr(name)
        return q.__class__(self, "{inner}[{name}]", kwargs=dict(inner=q, name=name))

    def call(self, q: Q, args: t.Sequence[object], kwargs: t.Dict[str, object]) -> Q:
        return q.__class__(
            self,
            "{inner}({args})",
            kwargs=dict(inner=q, args=QArgs(self, args, kwargs)),
        )

    def build(self, q: Q) -> t.Any:
        return q.__to_string__(self)


class QEvaluator(BuilderProtocol):
    uop_mapping = {
        "-": operator.neg,
        "not": operator.not_,
    }
    bop_mapping = {
        "and": lambda x, y: x and y,
        "or": lambda x, y: x or y,
        ">": operator.gt,
        ">=": operator.ge,
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
        "is": operator.is_,
        "is not": operator.is_not,
        "in": lambda x, y: x in y,
        "not in": lambda x, y: x not in y,
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
    }

    def uop(self, q: Q, name: str) -> Q:
        op = self.uop_mapping[name]
        val = op(getattr(q, "val", q))
        return q.__class__(self, val, kwargs=None)

    def bop(self, q: Q, name: str, right: Q) -> Q:
        op = self.bop_mapping[name]
        left_val = getattr(q, "val", q)
        right_val = getattr(right, "val", right)
        val = op(left_val, right_val)
        return q.__class__(self, val, kwargs=None)

    def getattr(self, q: Q, name: str) -> Q:
        ob = getattr(q, "val", q)
        return q.__class__(self, getattr(ob, name), kwargs=None)

    def getindex(self, q: Q, name: str) -> Q:
        ob = getattr(q, "val", q)
        return q.__class__(self, ob[getattr(name, "val", name)], kwargs=None)

    def call(self, q: Q, args: t.Sequence[object], kwargs: t.Dict[str, object]) -> Q:
        args = [getattr(x, "val", x) for x in args]
        kwargs = {k: getattr(x, "val", x) for k, x in kwargs.items()}
        val = q.val(*args, **kwargs)  # type: ignore
        return q.__class__(self, val, kwargs=None)

    def build(self, q: Q) -> t.Any:
        return q.val


def q(
    fmt_or_val: t.Union[str, object],
    builder: BuilderProtocol = QBuilder(),
    **kwargs: object
) -> Q:
    return Q(builder, fmt_or_val, kwargs=kwargs)
