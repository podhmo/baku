import graphql as g


Query = g.GraphQLObjectType(
    'Query',
    lambda: {
        'name': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
        'age': g.GraphQLField(g.GraphQLNonNull(g.GraphQLInt)),
    }
)
