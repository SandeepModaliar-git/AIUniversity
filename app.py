import uuid

from fastapi import FastAPI
from pydantic import BaseModel

from generate_learning_path import app

api = FastAPI()


class LearningRequest(BaseModel):
    query: str
    level: str


@api.post("/generate-learning-path")
def generate_learning_path(request: LearningRequest):

    initial_input = {
        "query": request.query,
        "level": request.level
    }

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    state = app.invoke(initial_input, config=config)

    return {
    "level": state["level"],
    "query": state["query"],
    "revised_query": state["revised_query"],
    "learning_path": state["learning_path"],
    "no_of_weeks" : len(state["learning_path"]),
    }