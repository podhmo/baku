import graphql as g


Article_Content = g.GraphQLObjectType(
    'Article_Content',
    lambda: {
        'abbrev': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
        'body': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
    }
)
Article_Comments_Content = g.GraphQLObjectType(
    'Article_Comments_Content',
    lambda: {
        'body': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
    }
)
Article_Comment = g.GraphQLObjectType(
    'Article_Comment',
    lambda: {
        'user': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
        'content': g.GraphQLField(Article_Comments_Content),
    }
)
Article = g.GraphQLObjectType(
    'Article',
    lambda: {
        'content': g.GraphQLField(Article_Content),
        'comments': g.GraphQLField(g.GraphQLList(Article_Comment)),
    }
)
Query = g.GraphQLObjectType(
    'Query',
    lambda: {
        'article': g.GraphQLField(Article),
    }
)
