import graphql as g


Person = g.GraphQLObjectType(
    'Person',
    lambda: {
        'name': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
        'age': g.GraphQLField(g.GraphQLNonNull(g.GraphQLInt)),
    }
)
