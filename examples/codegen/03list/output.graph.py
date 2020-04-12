import graphql as g


Parent = g.GraphQLObjectType(
    'Parent',
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
        'parents': g.GraphQLField(g.GraphQLList(Parent)),
    }
)
