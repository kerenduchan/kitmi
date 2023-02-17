from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from strawberry.fastapi import GraphQLRouter
from strawberry.schema import Schema
from starlette.middleware.cors import CORSMiddleware
from api.query import Query
from api.mutation import Mutation
from api.context import Context
from init_logging import init_logging
from db.init import init_db


def get_context():
    return Context()


init_db()
init_logging()

schema = Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
    max_age=3600,
)

app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    return RedirectResponse(url="/graphql")
