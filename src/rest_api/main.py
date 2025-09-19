from fastapi import FastAPI

from .routers import workloads, migrations, migration_targets

app = FastAPI(title="Migration API")

# uvicorn src.rest_api.main:app --reload
# http://127.0.0.1:8000/docs

app.include_router(workloads.router, prefix="/workloads",tags=["workloads"])
app.include_router(migration_targets.router, prefix="/migration_targets",tags=["migration_targets"])
app.include_router(migrations.router, prefix="/migrations",tags=["migrations"])