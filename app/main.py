from typing import Annotated, Any, Callable, Optional, TypedDict
from datetime import date
import operator

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Query, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class Task(TypedDict):
    id: int
    title: str
    completed: bool
    due: date

tasks : dict[int, Task] = {
    2: {
        "id": 2,
        "title": "buy milk",
        "completed": True,
        "due": date(2024, 5, 17)
    },
    1: {
        "id": 1,
        "title": "buy eggs",
        "completed": True,
        "due": date(2024, 5, 18)
    },
    0: {
        "id": 0,
        "title": "top up gas",
        "completed": False,
        "due": date(2024, 5, 16)
    },
    3: {
        "id": 3,
        "title": "complete math homework",
        "completed": False,
        "due": date(2024, 5, 13)
    },
    4: {
        "id": 4,
        "title": "make bed",
        "completed": True,
        "due": date(2024, 7, 1)
    },
    5: {
        "id": 5,
        "title": "pick up kids",
        "completed": False,
        "due": date(2024, 2, 27)
    },
}

# Mapping of operator prefixes to actual operator functions
operator_map = {
    'gt': operator.gt,
    'lt': operator.lt,
    'gte': operator.ge,
    'lte': operator.le,
    'eq': operator.eq,
    '': operator.eq
}

ADMIN_PASSWORD = "adminpassword"
security = HTTPBearer()

id_incr = max(tasks.keys())

def get_unique_id():
    global id_incr
    id_incr+=1
    return id_incr


def get_first_digit_i(s: str) -> int:
    found = 0
    for i in range(len(s)):
        if s[i].isdigit():
            found = i
            break
    return found

def parse_filter_params(
    id: list[str] = Query(None),
    due: list[str] = Query(None),
    completed: bool = Query(None)
) -> list[tuple[str, Callable[[Any, Any], bool], Any]]:
    filters = []
    if id is not None:
        for filt in id:
            digits_i = get_first_digit_i(filt)
            op_func = operator_map.get(filt[:digits_i])
            if op_func is None:
                raise HTTPException(status_code=400, detail=f"Invalid operator in id filter: {filt}")
            try:
                value = int(filt[digits_i:])
                filters.append(("id", op_func, value))
            except:
                raise HTTPException(status_code=400, detail=f"Invalid value for id filter: {filt}")
    if due is not None:
        for filt in due:
            digits_i = get_first_digit_i(filt)
            op_func = operator_map.get(filt[:digits_i])
            if op_func is None:
                raise HTTPException(status_code=400, detail=f"Invalid operator in due date filter: {filt}")
            try:
                value = date.fromisoformat(filt[digits_i:])
                filters.append(("due", op_func, value))
            except:
                raise HTTPException(status_code=400, detail=f"Invalid value for due date filter: {filt}")
    if completed is not None:
        filters.append(("completed", operator.eq, completed))

    return filters

def check_authorization(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != ADMIN_PASSWORD:
        raise HTTPException(status_code=401)
    return True

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World!"}

@app.get("/tasks")
def get_tasks(sortBy: Optional[str] = None, count: Optional[int] = None):
    global tasks
    res = list(tasks.values())
    try:
        if sortBy is not None:
            res = sorted(res, key=lambda t: t[sortBy])
        if count is not None:
            res = res[0:count]
    except:
        raise HTTPException(status_code=400)
    return res

@app.get("/tasks/{id}")
def get_task(id: int):
    global tasks
    if not id in tasks:
        raise HTTPException(status_code=400)
    return tasks[id]

@app.post("/tasks")
def create_task(
    title: Annotated[str, Body()],
    due: Annotated[date, Body()]
):
    global tasks
    id = get_unique_id()
    tasks[id] = {
        "id": id,
        "title": title,
        "completed": False,
        "due": due
    }

@app.put("/tasks/{id}")
def update_task(
    id: int,
    title: Annotated[Optional[str] , Body()] = None,
    due: Annotated[Optional[date], Body()] = None,
    completed: Annotated[Optional[bool], Body()] = None,
):
    global tasks
    task = tasks.get(id)
    if task is None:
        raise HTTPException(status_code=400)
    if title is not None:
        task["title"] = title
    if due is not None:
        task["due"] = due
    if completed is not None:
        task["completed"] = completed

@app.delete("/tasks", dependencies=[Security(check_authorization)])
def delete_tasks(
    filters: list[tuple[str, Callable[[Any, Any], bool], Any]] = Depends(parse_filter_params)
):
    global tasks
    to_delete = list(tasks.keys())
    for attr, op_func, value in filters:
        to_delete = [k for k in to_delete if op_func(tasks[k][attr], value)]
    for key in to_delete:
        tasks.pop(key)

