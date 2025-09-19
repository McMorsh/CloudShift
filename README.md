# CloudShift

This project is a migration manager with REST API built on Fast API.

---

## Requirements

- Python 3.10+
- Install dependencies:

```shell
pip install -r requirements.txt
```

---

## Running API

```shell
uvicorn src.rest_api.main:app --reload
```

- Server will start at: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

---

## Data Storage

All objects are stored as `.json` in `./data` folder:

```
data/
  migration_targets/
  migrations/
  workloads/
```

For reset state need to delete these files:

```bash
# Linux / macOS
rm -f ./data/workloads/*.json
rm -f ./data/migrations/*.json
rm -f ./data/migration_targets/*.json

# Windows PowerShell
Remove-Item -Path .\data\workloads\*.json -Force -ErrorAction SilentlyContinue
Remove-Item -Path .\data\migrations\*.json -Force -ErrorAction SilentlyContinue
Remove-Item -Path .\data\migration_targets\*.json -Force -ErrorAction SilentlyContinue
```

---

## Test

For the main task was used **pytest**, because it is clean and convenient:

```bash
pytest -vv -s
```

For API testing was used the request library(simple to use and convenient).
The tests check:

- Create a Workload
- Try to change workload IP (**ERROR**)
- Create a Migration Target
- Create a Migration
- Run the migration
- Check migration status

```bash
python tests/test_api.py 
```

---

## My Solutions

- Safe files writing with `os.replace`
- Repository pattern with CRUD was used to create a persistence layer
- Files are stored by their `id`, which is generated automatically in class
