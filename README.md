# Data Server [![CI](https://github.com/your-org/data-server/actions/workflows/main-ci.yml/badge.svg)](https://github.com/your-org/data-server/actions/workflows/main-ci.yml) [![PyPI version](https://img.shields.io/pypi/v/data-server.svg)](https://pypi.org/project/data-server/)

Spin up a fully functional **fake REST API** from a JSON or CSV file — **no code required**. Point the server at a file, and it auto-generates endpoints for CRUD operations with sensible defaults.

## ✨ Features
- Zero-config REST endpoints from JSON/CSV
- Sorting, filtering, pagination
- Auto IDs and timestamping (optional)
- Lightweight, pure-Python; powered by Werkzeug

## 📦 Installation
```bash
pip install data-server
```

## 🚀 Quickstart
```bash
python -m data_server --file examples/todos.json --port 8000
```
Now open http://localhost:8000 to explore the generated endpoints.

## ⚙️ CLI Options (common)
- `--file`: Path to JSON/CSV file (required)
- `--port`: Port to bind (default: 8000)
- `--id-name`: Primary key field name (default: id)
- `--timestamps/--no-timestamps`: Toggle created/updated fields

## 🧪 Development
```bash
# clone and install dev deps
pip install -e .[dev]

# format & lint
ruff format .
ruff check .

# type-check
mypy data_server

# tests
coverage run -m unittest discover -v -s tests
coverage report -m
```

## 🔁 Release & Publish
1. Bump the `version` in `pyproject.toml` (currently **1.0.0**).
2. Create a GitHub Release. The publish workflow uploads to PyPI using `PYPI_API_TOKEN` secret.

## 📄 License
MIT
