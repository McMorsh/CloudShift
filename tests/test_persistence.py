import pytest
import tempfile
from pathlib import Path

from src import (
    Credentials,
    MigrationTarget,
    CloudType,
    Migration,
    WorkloadRepository,
    MigrationTargetRepository,
    MigrationRepository,
    BusinessRuleError,
    DuplicateError,
    MigrationState, NotFoundError,
)
from tests.test_core import constructor_workload


# ---
# PERSISTENCE TESTS
# ---

@pytest.fixture
def tmpdir_repo():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


# Test class WorkloadRepository
def test_workload_repository_create_error(tmpdir_repo):
    workload_repository_test = WorkloadRepository(tmpdir_repo)
    workload_test = constructor_workload(ip="1.1.1.1")

    workload_repository_test.create(workload_test)
    with pytest.raises(DuplicateError):
        workload_repository_test.create(constructor_workload(ip="1.1.1.1"))


def test_workload_repository_get_error(tmpdir_repo):
    workload_repository_test = WorkloadRepository(tmpdir_repo)

    with pytest.raises(NotFoundError):
        workload_repository_test.get("1.1.1.2")


def test_workload_repository_update_error(tmpdir_repo):
    workload_repository_test = WorkloadRepository(tmpdir_repo)
    workload_test = constructor_workload(ip="1.1.1.1")

    workload_repository_test.create(workload_test)
    workload_error = constructor_workload(ip="1.1.1.2")
    workload_error.id = workload_test.id

    with pytest.raises(BusinessRuleError):
        workload_repository_test.update(workload_error)


def test_workload_repository_crud(tmpdir_repo):
    workload_repository_test = WorkloadRepository(tmpdir_repo)
    workload_test = constructor_workload(ip="1.1.1.1")

    # create
    workload_repository_test.create(workload_test)
    assert workload_repository_test.get(workload_test.id).ip == workload_test.ip
    assert workload_repository_test.get(workload_test.id).credentials.username == "user"

    # update
    workload_new = workload_test
    workload_new.credentials = Credentials("u", "p", "d")
    workload_repository_test.update(workload_new)
    assert workload_repository_test.get(workload_test.id).ip == workload_test.ip
    assert workload_repository_test.get(workload_test.id).credentials.username == "u"

    # delete
    workload_repository_test.delete(workload_test.id)
    with pytest.raises(NotFoundError):
        workload_repository_test.get(workload_test.id)


# Test class MigrationTargetRepository
def test_migration_target_repository_get_error(tmpdir_repo):
    migration_target_repository = MigrationTargetRepository(tmpdir_repo)
    with pytest.raises(NotFoundError):
        migration_target_repository.get("1.1.1.1")


def test_migration_target_repository_update_error(tmpdir_repo):
    migration_target_repository = MigrationTargetRepository(tmpdir_repo)
    target = MigrationTarget(
        cloud_type=CloudType.AZURE,
        cloud_credentials=Credentials("u", "p", "d"),
        target_vm=constructor_workload(ip="0.0.0.0"),
    )
    with pytest.raises(NotFoundError):
        migration_target_repository.update(target)


def test_migration_target_repository_crud(tmpdir_repo):
    migration_target_repository = MigrationTargetRepository(tmpdir_repo)
    target = MigrationTarget(
        cloud_type=CloudType.AZURE,
        cloud_credentials=Credentials("u", "p", "d"),
        target_vm=constructor_workload(ip="0.0.0.0"),
    )

    # create
    migration_target_repository.create(target)
    assert migration_target_repository.get(target.id).cloud_type == CloudType.AZURE

    # update
    updated = MigrationTarget(
        cloud_type=CloudType.VSPHERE,
        cloud_credentials=Credentials("u2", "p2", "d2"),
        target_vm=constructor_workload(ip="1.1.1.1"),
        id=target.id,
    )
    migration_target_repository.update(updated)
    assert migration_target_repository.get(target.id).cloud_type == CloudType.VSPHERE


# Test class MigrationRepository
def test_migration_repository_get_error(tmpdir_repo):
    migration_repository = MigrationRepository(tmpdir_repo)
    with pytest.raises(NotFoundError):
        migration_repository.get("1.1.1.1")


def test_migration_repository_update_error(tmpdir_repo):
    migration_repository = MigrationRepository(tmpdir_repo)
    src = constructor_workload(ip="0.0.0.0")
    target = MigrationTarget(
        cloud_type=CloudType.VCLOUD,
        cloud_credentials=Credentials("u", "p", "d"),
        target_vm=constructor_workload(ip="1.1.1.1"),
    )
    migration = Migration(
        selected_mount_points=[src.storage[0]],
        source=src,
        migration_target=target,
    )
    with pytest.raises(NotFoundError):
        migration_repository.update(migration)


def test_migration_repository_crud(tmpdir_repo):
    migration_repository = MigrationRepository(tmpdir_repo)
    src = constructor_workload(ip="0.0.0.0")
    target = MigrationTarget(
        cloud_type=CloudType.VCLOUD,
        cloud_credentials=Credentials("u", "p", "d"),
        target_vm=constructor_workload(ip="1.1.1.1"),
    )
    migration = Migration(
        selected_mount_points=[src.storage[0]],
        source=src,
        migration_target=target,
    )

    # create
    migration_repository.create(migration)
    assert migration_repository.get(migration.id).source.ip == "0.0.0.0"

    # update
    migration.state = MigrationState.SUCCESS
    migration_repository.update(migration)
    assert migration_repository.get(migration.id).state == MigrationState.SUCCESS
