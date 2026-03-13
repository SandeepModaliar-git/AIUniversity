import uuid

from fastapi import FastAPI
from pydantic import BaseModel

from generate_learning_path import app

api = FastAPI()


class LearningRequest(BaseModel):
    query: str
    level: str
    duration: str


@api.post("/generate-learning-path")
def generate_learning_path(request: LearningRequest):

    initial_input = {
        "query": request.query,
        "level": request.level,
        "duration" : request.duration
    }

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    state = app.invoke(initial_input, config=config)

    return {
        "level" : state["level"],
        "query" : state["query"],
        "duration" : state["duration"],
        "learning_plan" : state["final_roadmap"]
    }