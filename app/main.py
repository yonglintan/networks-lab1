from typing import Optional, Union
from copy import deepcopy

from fastapi import Depends, FastAPI
from datetime import datetime

tasks = {
    0: {
        "id": 0,
        "title": "buy milk",
        "completed": False,
        "due": datetime(2024, 5, 17)
    },
    1: {
        "id": 1,
        "title": "buy eggs",
        "completed": False,
        "due": datetime(2024, 5, 18)
    },
    2: {
        "id": 2,
        "title": "top up gas",
        "completed": False,
        "due": datetime(2024, 5, 16)
    },
    3: {
        "id": 3,
        "title": "complete math homework",
        "completed": False,
        "due": datetime(2024, 5, 13)
    },
    4: {
        "id": 4,
        "title": "make bed",
        "completed": False,
        "due": datetime(2024, 7, 1)
    },
    5: {
        "id": 5,
        "title": "pick up kids",
        "completed": False,
        "due": datetime(2024, 2, 27)
    },
}

id_incr = max(tasks.keys())

def get_unique_id():
    global id_incr
    return ++id_incr


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World!"}

@app.get("/tasks")
def get_tasks(sortBy: Optional[str] = None, limit: Optional[int] = None):
    global tasks
    res = list(tasks.values())
    print("limit:", limit)
    if sortBy is not None:
        res = sorted(res, key=lambda t: t[sortBy])
    if limit is not None:
        print("limit:", limit)
        res = res[0:limit]
    return res

@app.get("/tasks/{id}")
def get_task(id: int):
    global tasks
    return tasks[id]
