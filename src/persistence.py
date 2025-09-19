from pathlib import Path
from typing import List

from .exceptions import DuplicateError, NotFoundError, BusinessRuleError
from .utils import read_json, write_json
from .core import Workload, MigrationTarget, Migration


class Repository:
    """
    Base repository class: storing each entity in a separate one .json file.
    """

    def __init__(self, dir: Path):
        self.dir = dir
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, id_obj: str):
        return self.dir / f"{id_obj}.json"

    def delete(self, id_obj: str):
        path = self._path(id_obj)
        if not path.exists():
            raise NotFoundError(f"Object {id_obj} not found")
        path.unlink()

    @staticmethod
    def _read_json(path: Path) -> dict:
        return read_json(path)

    @staticmethod
    def _write_json(path: Path, obj: dict) -> None:
        return write_json(path, obj)


class WorkloadRepository(Repository):
    """
    CRUD for Workload
    Unique index of IP and the prohibition of changing the IP during the update
    """

    def list_all(self) -> List[Workload]:
        result: List[Workload] = []
        for filename in self.dir.iterdir():
            if filename.is_file() and filename.suffix == ".json":
                try:
                    result.append(self.get(filename.stem))
                except NotFoundError:
                    pass

        return result

    # CRUD
    def create(self, workload: Workload) -> Workload:
        for existing in self.list_all():
            if existing.ip == workload.ip:
                raise DuplicateError(f"Workload {workload.ip} {workload.id} already exists")

        path = self._path(workload.id)
        self._write_json(path, workload.to_dict())

        return workload

    def get(self, id_obj) -> Workload:
        path = self._path(id_obj)
        if not path.exists():
            raise NotFoundError(f"File {id_obj} not found")

        obj = self._read_json(path)

        return Workload.from_dict(obj)

    def update(self, workload: Workload) -> Workload:
        curr = self.get(workload.id)
        if workload.ip != curr.ip:
            raise BusinessRuleError("Ip cannot be changed for existing workload")

        path = self._path(workload.id)
        self._write_json(path, workload.to_dict())

        return workload


class MigrationTargetRepository(Repository):
    """
    CRUD for Migration Targets
    """

    def list_all(self) -> List[MigrationTarget]:
        result: List[MigrationTarget] = []

        for filename in self.dir.iterdir():
            if filename.is_file() and filename.suffix == ".json":
                try:
                    result.append(self.get(filename.stem))
                except NotFoundError:
                    pass

        return result

    # CRUD
    def create(self, target: MigrationTarget) -> MigrationTarget:
        path = self._path(target.id)
        self._write_json(path, target.to_dict())

        return target

    def get(self, id_obj: str) -> MigrationTarget:
        path = self._path(id_obj)
        if not path.exists():
            raise NotFoundError(f"MigrationTarget {id_obj} not found")

        obj = self._read_json(path)

        return MigrationTarget.from_dict(obj)

    def update(self, target: MigrationTarget) -> MigrationTarget:
        path = self._path(target.id)
        if not path.exists():
            raise NotFoundError(f"MigrationTarget {target.id} not found")

        return self.create(target)


class MigrationRepository(Repository):
    """
    CRUD for Migration Repository
    """

    def list_all(self) -> List[Migration]:
        result: List[Migration] = []

        for filename in self.dir.iterdir():
            if filename.is_file() and filename.suffix == ".json":
                try:
                    result.append(self.get(filename.stem))
                except NotFoundError:
                    pass

        return result

    # CRUD
    def create(self, migration: Migration) -> Migration:
        path = self._path(migration.id)
        self._write_json(path, migration.to_dict())

        return migration

    def get(self, id_obj: str) -> Migration:
        path = self._path(id_obj)
        if not path.exists():
            raise NotFoundError(f"Migration {id_obj} not found")

        obj = self._read_json(path)

        return Migration.from_dict(obj)

    def update(self, migration: Migration) -> Migration:
        path = self._path(migration.id)
        if not path.exists():
            raise NotFoundError(f"Migration {migration.id} not found")

        self._write_json(path, migration.to_dict())

        return migration
