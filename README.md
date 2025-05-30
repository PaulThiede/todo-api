# ToDo API

A RESTful API for the management of ToDo items.  
This project provides user-based authentication, filtering, sorting and pagination for task management.

## Features

- **JWT authentication**
  Securing all endpoints via JSON web tokens with login, registration and user management.

- **CRUD functionality for tasks**
  Supports the creation, reading, updating and deletion of ToDo items.

- **Dynamic filtering**
  Allows filtering of tasks via:
  - Title (substring)
  - Description (substring)
  - Completed status (`true`/`false`)
  - Creation period (`created_since`, `created_until`)

- **Flexible sorting**
  Sorts results by `title`, `description` or `created_at` in any order (`asc`, `desc` per field).

- **Pagination**
  Returns tasks page by page, controllable via `page` and `limit`.

---

## Installation

```bash
git clone https://github.com/PaulThiede/todo-api
docker-compose build
docker-compose up -d

docker-compose logs -f backend
