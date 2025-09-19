from fastapi import APIRouter, HTTPException
from pathlib import Path

from src import MigrationRepository, Migration, NotFoundError, BusinessRuleError

router = APIRouter()

migration_repository = MigrationRepository(Path("./data/migrations"))


@router.post("/")
def create_migration(migration_dict: dict):
    migration = Migration.from_dict(migration_dict)
    return migration_repository.create(migration).to_dict()


@router.get("/{migration_id}")
def get_migration(migration_id: str):
    try:
        return migration_repository.get(migration_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/")
def list_migrations():
    return [m.to_dict() for m in migration_repository.list_all()]


@router.put("/{migration_id}")
def update_migration(migration_id: str, migration_dict: dict):
    try:
        migration = Migration.from_dict(migration_dict)
        migration.id = migration_id
        return migration_repository.update(migration).to_dict()
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{migration_id}")
def delete_migration(migration_id: str):
    try:
        migration_repository.delete(migration_id)
        return {"message": f"Migration {migration_id} deleted"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{migration_id}/run")
def run_migration(migration_id: str):
    try:
        migration = migration_repository.get(migration_id)
        migration.run(min_to_sleep=0)
        migration_repository.update(migration)
        return {"status": migration.state.value}
    except BusinessRuleError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{migration_id}/status")
def migration_status(migration_id: str):
    try:
        return {"status": migration_repository.get(migration_id).state.value}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
