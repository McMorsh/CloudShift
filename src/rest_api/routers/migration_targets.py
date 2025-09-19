from fastapi import APIRouter, HTTPException
from pathlib import Path

from src import MigrationTarget, MigrationTargetRepository, NotFoundError

router = APIRouter()

migration_target_repository = MigrationTargetRepository(Path("./data/migration_targets"))


@router.post("/")
def create_migration_target(obj: dict):
    migration_target = MigrationTarget.from_dict(obj)
    return migration_target_repository.create(migration_target).to_dict()


@router.get("/{migration_target_id}")
def read_migration_target(id_obj: str):
    try:
        return migration_target_repository.get(id_obj).to_dict()
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/")
def list_migration_targets():
    return [mt.to_dict() for mt in migration_target_repository.list_all()]


@router.put("/{migration_target_id}")
def update_migration_target(migration_target_id: str, obj: dict):
    try:
        migration_target = MigrationTarget.from_dict(obj)
        migration_target.id = migration_target_id
        return migration_target_repository.update(migration_target).to_dict()
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{migration_target_id}")
def delete_migration_target(migration_target_id: str):
    try:
        migration_target_repository.delete(migration_target_id)
        return {"message": f"Migration {migration_target_id} deleted"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
