# Data Server

[![CI](https://github.com/your-org/data-server/actions/workflows/main-ci.yml/badge.svg)](https://github.com/your-org/data-server/actions/workflows/main-ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/data-server.svg)](https://pypi.org/project/data-server/)

Spin up a fake REST API from a JSON or CSV file with zero framework setup.

Data Server reads your file, exposes routes automatically, supports CRUD for list resources, and writes changes back to disk.

---

## Table of Contents

- [Why Data Server](#why-data-server)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [How Routing Works](#how-routing-works)
- [Request and Response Behavior](#request-and-response-behavior)
- [Query Parameters (filter, sort, paging)](#query-parameters-filter-sort-paging)
- [CLI Reference](#cli-reference)
- [Data File Requirements](#data-file-requirements)
- [Development](#development)
- [Release and Publish (PyPI)](#release-and-publish-pypi)
- [License](#license)

---

## Why Data Server

- Generate an API from existing mock data in seconds.
- Test frontend flows without hand-writing backend endpoints.
- Simulate realistic behavior (pagination, sorting, filtering, latency).
- Keep data local and editable through HTTP requests.

---

## Installation

```bash
pip install data-server
```

You can run it either as a module or a CLI command:

```bash
python -m mock_data_server <file>
# or
data-server <file>
```

---

## Quick Start

1. Create a sample JSON file:

```json
{
  "todos": [
    { "id": 1, "title": "Write docs", "done": false },
    { "id": 2, "title": "Ship feature", "done": false }
  ]
}
```

2. Start the server:

```bash
data-server ./todos.json --port 8000
```

3. Try requests:

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/todos
curl http://127.0.0.1:8000/todos/1
```

---

## How Routing Works

- `GET /` returns discovered routes and supported methods.
- Each top-level list becomes a collection endpoint (for example, `todos` -> `/todos`).
- Collection endpoints support `GET` and `POST`.
- Item endpoints support `GET`, `PUT`, `PATCH`, and `DELETE`.

If you provide `--url-path-prefix /api/v1`, all routes are served under that prefix.

---

## Request and Response Behavior

- `POST` returns `201`.
- `DELETE` returns `204` when successful.
- Other successful requests return `200`.
- CORS header `Access-Control-Allow-Origin: *` is included.
- Errors are returned as JSON:

```json
{
  "error": {
    "description": "...",
    "code": 400,
    "details": "..."
  }
}
```

You can add custom headers to every response with:

```bash
--additional-headers "X-Limit:20;X-Source:mock"
```

---

## Query Parameters (filter, sort, paging)

Collection `GET` requests support:

- **Filtering**: any extra query keys are treated as exact-match filters.
- **Sorting**: `sort_by=<field>` and `order=asc|desc`.
- **Pagination**:
  - `page` (starts at `0`)
  - `size` (default comes from `--page-size`, default value is `10`)

Example:

```bash
curl "http://127.0.0.1:8000/todos?done=false&sort_by=title&order=asc&page=0&size=5"
```

You can rename these query parameter names via CLI flags such as `--page-param-name`, `--sort-param-name`, `--order-param-name`, and `--size-param-name`.

---

## CLI Reference

Usage:

```bash
data-server <file> [options]
```

Required positional argument:

- `file`: Path to a `.json` or `.csv` file.

Server options:

- `--host` (default: `127.0.0.1`)
- `--port` (default: `2000`)
- `--url-path-prefix`
- `--static-folder`
- `--static-url-prefix` (default: `static`)
- `--additional-headers`
- `--sleep-before-request` (milliseconds)

Data/controller options:

- `--id-name` (default: `id`)
- `--auto-generate-ids` / `--no-auto-generate-ids`
- `--use-timestamps` / `--no-use-timestamps`
- `--created-at-key-name` (default: `created_at`)
- `--updated-at-key-name` (default: `updated_at`)
- `--page-size` (default: `10`)
- `--page-param-name` (default: `page`)
- `--sort-param-name` (default: `sort_by`)
- `--order-param-name` (default: `order`)
- `--size-param-name` (default: `size`)

---

## Data File Requirements

### JSON

- Must be valid JSON.
- Top-level object keys typically map to endpoint paths.
- List values are treated as resources that support CRUD.
- Changes are persisted back to the same file.

### CSV

- The CSV filename (without extension) becomes the route name.
- Rows are exposed as a single collection.
- Values are read as strings.
- Changes are written back to the same CSV file.

---

## Development

```bash
# install with dev dependencies
pip install -e .[dev]

# format + lint
ruff format .
ruff check .

# type-check
mypy --strict mock_data_server

# run tests
coverage run -m unittest discover -v -s tests
coverage report -m
```

Main CI runs on push/PR to `main`.

---

## Release and Publish (PyPI)

Publishing is automated through GitHub Actions after a successful CI run on `main`.

1. Bump `version` in `pyproject.toml`.
2. Ensure repo secret `PYPI_API_TOKEN` is configured.
3. Merge to `main`.
4. CI passes, then the publish workflow uploads to PyPI.

---

## License

MIT
