import strawberry
import fastapi
from starlette.middleware.cors import CORSMiddleware
import gql.query
import gql.mutation
import gql.context
import init_logging

init_logging.init_logging()

schema = strawberry.Schema(query=gql.query.Query, mutation=gql.mutation.Mutation)
graphql_app = strawberry.fastapi.GraphQLRouter(schema, context_getter=gql.context.get_context)

app = fastapi.FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
    max_age=3600,
)

app.include_router(graphql_app, prefix="/graphql")
