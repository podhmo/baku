import dataclasses
import typing as t
from .detect import Result, Object, generate_annotations, TypeInfo
from ._module import Symbol, Module

# TODO: list
# TODO: typing
# TODO: query
# TODO: custom query attribute (with q)


AnnotationMap = t.Dict[
    str, t.Any
]  # {"": {"before": {"name": ""}, "after": {"name": ""}}}


def emit(
    result: Result,
    *,
    m: t.Optional[Module] = None,
    toplevel_name: str = "Query",
    annotations: t.Optional[AnnotationMap] = None,
) -> Module:
    emitter = get_emitter(m=m)
    ctx = build_context(
        emitter.g, result, annotations=annotations, toplevel_name=toplevel_name
    )
    return emitter.emit(ctx, result)


def get_emitter(*, m: t.Optional[Module] = None) -> "Emitter":
    m = m or Module()
    m.toplevel = m.submodule()
    g = m.toplevel.import_("graphql", as_="g")  # xxx
    m.sep()
    return Emitter(m, g)


def build_context(
    g: Symbol,
    result: Result,
    *,
    toplevel_name: str = "Query",
    annotations: t.Optional[AnnotationMap] = None,
) -> "Context":
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


@dataclasses.dataclass
class Context:
    g: Symbol  # todo: omit
    type_map: t.Dict[str, str]
    name_map: t.Dict[str, t.Type[t.Any]]

    def graphql_type(self, info: TypeInfo) -> t.Any:
        if hasattr(info, "base") and info.base is t.Optional:
            return self.type_map[info.item.type]

        if hasattr(info, "type"):
            return self.g.GraphQLNonNull(self.type_map[info.type])
        else:
            return Symbol(self.node_name(info))

    def node_name(self, info: TypeInfo) -> str:
        return self.name_map["/".join(info.path)]


class Emitter:
    def __init__(self, m: Module, g: Symbol):
        self.m = m
        self.g = g

    def emit(self, ctx: Context, result: Result) -> Module:
        m = self.m
        g = self.g
        result = result

        # todo: use lazy string
        for info in result.history:
            if not isinstance(info, Object):
                continue

            name = ctx.node_name(info)  # xxx
            m.stmt("{} = {}(", name, g.GraphQLObjectType)
            with m.scope():
                m.stmt("{!r},", name)
                m.stmt("lambda: {")
                with m.scope():
                    for fieldname, field in info.props.items():
                        m.stmt(
                            "{!r}: {},",
                            fieldname,
                            g.GraphQLField(ctx.graphql_type(field)),
                        )
                m.stmt("}")
            m.stmt(")")
        return m
