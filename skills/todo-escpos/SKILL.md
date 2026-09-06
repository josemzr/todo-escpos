---
name: todo-escpos
description: Manage work and personal tasks, including listing, creating, updating, completing, deleting, and printing them through the Todo ESC/POS HTTP API.
---

# Todo ESC/POS

Use this skill when the user wants to manage or print tasks in Todo ESC/POS.

## Configuration

Read the application base URL from `TODO_ESCPOS_URL`. If it is unavailable, ask
the user for the URL. Never guess a public URL. The API uses JSON and is rooted
at `${TODO_ESCPOS_URL}/api`.

## Workflow

1. Translate the user's request into one API operation from the reference below.
2. For create or update operations, validate that `priority` is `HIGH`, `MEDIUM`,
   or `LOW`, and that `tag` is `WORK` or `PERSONAL`.
3. Use dates in `YYYY-MM-DD` format.
4. Confirm destructive bulk operations with the user before calling them.
5. Report the API result plainly. If printing returns an error, explain that the
   task operation may still have succeeded.

## API reference

- List active tasks: `GET /api/tasks`
- Filter tasks: `GET /api/tasks?tag=WORK|PERSONAL&completed=true|false`
- Get one task: `GET /api/tasks/{id}`
- Create: `POST /api/tasks` with `name`, `due_date`, and optional `description`,
  `priority`, `tag`, `print_flag`
- Update: `PATCH /api/tasks/{id}` with any task fields
- Complete: `POST /api/tasks/{id}/complete`
- Delete: `DELETE /api/tasks/{id}`
- Print: `POST /api/tasks/{id}/print`
- Complete active tasks: `POST /api/tasks/complete-all`, optionally with
  `?tag=WORK` or `?tag=PERSONAL`

Send `Content-Type: application/json` for requests with a body. Treat non-2xx
responses as failures and relay the JSON `error` field.
