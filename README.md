# Networks Lab 1

Basic task management API using FastAPI, for Lab 1 of 50.012 Networks.

## Requirements

- Docker

## Quickstart

From the project's root directory, run the server with the command:

```bash
docker compose up
```

## Tests

To run tests, ensure that the server is running. Then, enter a terminal in the container by running the commands:

```
docker exec -it lab1-fastapi-1 /bin/bash
```

From here, run the tests with:

```
pytest -v

# Alternatively, also include the -s flag to see the responses printed:
pytest -vs
```

## Endpoints

- `GET /tasks`
  - Returns all tasks
  - Supports the query parameters `sortBy` and `count`
- `GET /tasks/{id}`
  - Returns a single task with id `id`
- `POST /tasks`
  - Creates a new task
  - Request body contains the fields:
    - `title` (required): string title for the task
    - `due` (required): due date for the task, in the format YYYY-MM-DD
    - `completed` (optional): boolean representing whether or not the task is completed. Defaults to `False`.
- `PUT /tasks/{id}`
  - Modifies an existing task specified by `id`
  - Request body contains the fields:
    - `title` (required): string title for the task
    - `due` (required): due date for the task, in the format YYYY-MM-DD
    - `completed` (required): boolean representing whether or not the task is completed
- `DELETE /tasks`
  - Deletes all tasks matching the conditions specified in the query parameters
  - Requires authentication with the Authorization header. Refer to Completed Challenges section for password.
  - Query parameters:
    - `id`: Filter by id. Specify in format `{operator}{int}`. Supported operators: `lt`, `lte`, `eq`, `gt`, `gte`. Supports multiple filters. E.g. `id=gt2&id=lte4`
    - `due`: Filter by due date. Specify in format `{operator}{YYYY-MM-DD}`. Supported operators: `lt`, `lte`, `eq`, `gt`, `gte`. Supports multiple filters. E.g. `id=gt2024-01-01&id=lte2025-02-02`
    - `completed`: Filter by completed. Supports values `true` or `false`.

## Completed Challenges

- Batch delete of resources matching a certain condition: `DELETE /tasks` endpoint.
- Authorization through inspecting the request headers: `DELETE /tasks` requires authorization through headers. Authorized through `bearer adminpassword` in Authorization header.

## Idempotent Routes

- GET
  - Get requests by definition do not change the resource state
  - Verify by sending multiple `curl -X 'GET' 'http://localhost:8000/tasks'`
- PUT
  - Replaces the entire resource to desired state. If resource is already in desired state, no change happens.
  - Verify by sending multiple `curl -X 'PUT' 'http://localhost:8000/tasks/1' -H 'Content-Type: application/json' -d '{"title": "string", "due": "2025-02-18", "completed": true}`
- DELETE
  - Once the items matching the filters have been deleted, new requests with the same filter cannot delete more items.
  - Verify by sending multiple `curl -X 'DELETE' 'http://localhost:8000/tasks?id=lt2'`
