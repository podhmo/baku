import graphql as g


_Zero = g.GraphQLObjectType(
    '_Zero',
    lambda: {

    }
)
Query = g.GraphQLObjectType(
    'Query',
    lambda: {
        'name': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
        'age': g.GraphQLField(g.GraphQLNonNull(g.GraphQLInt)),
        'additionals': g.GraphQLField(_Zero),
    }
)