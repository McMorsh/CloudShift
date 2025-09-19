from fastapi import HTTPException, APIRouter
from pathlib import Path

from src import Workload, WorkloadRepository, DuplicateError, BusinessRuleError, NotFoundError

router = APIRouter()

workload_repository = WorkloadRepository(Path("./data/workloads"))


@router.post("/")
def create_workload(workload_dict: dict):
    try:
        workload = Workload.from_dict(workload_dict)
        return workload_repository.create(workload).to_dict()
    except DuplicateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessRuleError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{workload_id}")
def get_workload(workload_id: str):
    try:
        return workload_repository.get(workload_id).to_dict()
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/")
def list_workload():
    return [workload.to_dict() for workload in workload_repository.list_all()]


@router.put("/{workload_id}")
def update_workload(workload_id: str, obj: dict):
    try:
        workload = Workload.from_dict(obj)
        workload.id = workload_id
        return workload_repository.update(workload).to_dict()
    except BusinessRuleError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DuplicateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{workload_id}")
def delete_workload(workload_id: str):
    try:
        workload_repository.delete(workload_id).to_dict()
        return {"status": "deleted"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
