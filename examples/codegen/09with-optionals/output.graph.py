import graphql as g


Member = g.GraphQLObjectType(
    'Member',
    lambda: {
        'name': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
        'age': g.GraphQLField(g.GraphQLNonNull(g.GraphQLInt)),
        'nickname': g.GraphQLField(g.GraphQLString),
    }
)
Query = g.GraphQLObjectType(
    'Query',
    lambda: {
        'members': g.GraphQLField(g.GraphQLList(Member)),
    }
)
