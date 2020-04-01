import graphql as g


Person = g.GraphQLObjectType(
    'Person',
    lambda: {
        'name': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
        'age': g.GraphQLField(g.GraphQLNonNull(g.GraphQLInt)),
    }
)
Query = g.GraphQLObjectType(
    'Query',
    lambda: {
        'name': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
        'age': g.GraphQLField(g.GraphQLNonNull(g.GraphQLInt)),
        'father': g.GraphQLField(Person),
        'mother': g.GraphQLField(Person),
    }
)
