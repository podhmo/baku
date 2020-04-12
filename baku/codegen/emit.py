import dataclasses
import typing as t
from .detect import Result, Object, generate_annotations, TypeInfo
from ._module import Symbol, Module

# TODO: list
# TODO: typing
# TODO: query
# TODO: custom query attribute (with q)


class Module(PythonModule, CodeObjectModuleMixin):
    pass


AnnotationMap = t.Dict[
    str, t.Any
]  # {"": {"before": {"name": ""}, "after": {"name": ""}}}


@dataclasses.dataclass
class Context:
    g: Symbol
    type_map: t.Dict[str, str]
    name_map: t.Dict[str, t.Type[t.Any]]


def to_graphql_type(
    info: TypeInfo,
    *,
    type_map: t.Dict[t.Type[t.Any], t.Type[t.Any]],
    name_map: t.Dict[str, str],
    g: Symbol
) -> t.Any:
    if hasattr(info, "base") and info.base is t.Optional:
        return type_map[info.item.type]

    if hasattr(info, "type"):
        return g.GraphQLNonNull(type_map[info.type])
    else:
        return Symbol(name_map["/".join(info.path)])  # xxx


def emit(
    result: Result,
    *,
    m: t.Optional[Module] = None,
    toplevel_name: str = "Query",
    annotations: t.Optional[AnnotationMap] = None
) -> Module:

    m = m or Module()
    m.toplevel = m.submodule()
    g = m.toplevel.import_("graphql", as_="g")
    m.sep()

    ctx = build_context(g, result, annotations=annotations, toplevel_name=toplevel_name)
    Emitter(ctx).emit(m, result)
    return m


def build_context(
    g: Symbol,
    result: Result,
    *,
    toplevel_name: str = "Query",
    annotations: t.Optional[AnnotationMap] = None
) -> Context:
    type_map = {
        str: g.GraphQLString,
        int: g.GraphQLInt,
        bool: g.GraphQLBool,
    }

    default_annotations = generate_annotations(result, toplevel_name=toplevel_name)
    name_map = {
        k: v.get("after", v["before"])["name"] for k, v in default_annotations.items()
    }
    if annotations is not None:
        name_map.update(
            {k: v.get("after", v["before"])["name"] for k, v in annotations.items()}
        )
    return Context(g=g, type_map=type_map, name_map=name_map)


class Emitter:
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def emit(self, m: Module, result: Result) -> None:
        ctx = self.ctx
        g = ctx.g
        name_map = ctx.name_map
        type_map = ctx.type_map

        # todo: use lazy string
        for info in result.history:
            if not isinstance(info, Object):
                continue

            name = name_map["/".join(info.path)]  # xxx
            m.stmt("{} = {}(", name, g.GraphQLObjectType)
            with m.scope():
                m.stmt("{!r},", name)
                m.stmt("lambda: {")
                with m.scope():
                    for fieldname, field in info.props.items():
                        m.stmt(
                            "{!r}: {},",
                            fieldname,
                            g.GraphQLField(
                                to_graphql_type(
                                    field, type_map=type_map, name_map=name_map, g=g
                                )
                            ),
                        )
                m.stmt("}")
            m.stmt(")")
        return m
