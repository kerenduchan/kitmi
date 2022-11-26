import strawberry
import fastapi
import gql.query
import gql.mutation
import gql.context


schema = strawberry.Schema(query=gql.query.Query, mutation=gql.mutation.Mutation)
graphql_app = strawberry.fastapi.GraphQLRouter(schema, context_getter=gql.context.get_context)

app = fastapi.FastAPI()
app.include_router(graphql_app, prefix="/graphql")
