import graphql as g


Content = g.GraphQLObjectType(
    'Content',
    lambda: {
        'abbrev': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
        'body': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
    }
)
ContentDup1 = g.GraphQLObjectType(
    'ContentDup1',
    lambda: {
        'body': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
    }
)
Comment = g.GraphQLObjectType(
    'Comment',
    lambda: {
        'user': g.GraphQLField(g.GraphQLNonNull(g.GraphQLString)),
        'content': g.GraphQLField(ContentDup1),
    }
)
Article = g.GraphQLObjectType(
    'Article',
    lambda: {
        'content': g.GraphQLField(Content),
        'comments': g.GraphQLField(g.GraphQLList(Comment)),
    }
)
Query = g.GraphQLObjectType(
    'Query',
    lambda: {
        'article': g.GraphQLField(Article),
    }
)
