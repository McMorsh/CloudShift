import pytest

from src import (
    Credentials,
    MountPoint,
    Workload,
    MigrationTarget,
    CloudType,
    Migration,
    BusinessRuleError,
    MigrationState
)


# ---
# CORE TESTS
# ---

# Test dataclass Credentials
def test_credentials_error():
    with pytest.raises(BusinessRuleError):
        Credentials(username="", password="123", domain="test")
    with pytest.raises(BusinessRuleError):
        Credentials(username="user", password="", domain="test")


def test_credentials_error_and_constructor():
    credentials = Credentials(username="user", password="123", domain="test")

    assert credentials.username == "user"
    assert credentials.password == "123"
    assert credentials.domain == "test"


# Test dataclass MountPoint
def test_mount_point_error():
    with pytest.raises(BusinessRuleError):
        MountPoint(name="", total_size=100)
    with pytest.raises(BusinessRuleError):
        MountPoint(name="D:\\", total_size=-5)


def test_mount_point_constructor():
    mp = MountPoint(name="D:\\", total_size=100)

    assert mp.total_size == 100
    assert mp.name == "D:\\"


# Test dataclass Workload
def constructor_workload(credentials=None, ip="0.0.0.0"):
    if credentials is None:
        credentials = Credentials("user", "password", "domain")
    storage = [MountPoint("D:\\", 100), MountPoint("E:\\", 200)]

    return Workload(ip=ip, credentials=credentials, storage=storage)


def test_workload_error():
    with pytest.raises(BusinessRuleError):
        constructor_workload(ip="")
    with pytest.raises(BusinessRuleError):
        constructor_workload(credentials=["user", "password", "domain"])


def test_workload_constructor_and_dict():
    workload_test = constructor_workload()

    workload_dict = workload_test.to_dict()
    workload_test_2 = Workload.from_dict(workload_dict)

    assert workload_test.id == workload_test_2.id
    assert workload_test.ip == workload_test_2.ip
    assert workload_test_2.credentials.username == "user"


# Tests dataclass MigrationTarget
def constructor_migration_target(cloud_type=None, credentials=None, ip=None):
    if cloud_type is None:
        cloud_type = CloudType.AWS
    if credentials is None:
        credentials = Credentials("user", "password", "domain")
    if ip is None:
        ip = "1.1.1.1"

    return MigrationTarget(
        cloud_type=cloud_type,
        cloud_credentials=credentials,
        target_vm=constructor_workload(ip=ip),
    )


def test_migration_target_error():
    with pytest.raises(BusinessRuleError):
        constructor_migration_target(cloud_type="AWS")
    with pytest.raises(BusinessRuleError):
        constructor_migration_target(credentials=["user", "password", "domain"])
    with pytest.raises(BusinessRuleError):
        constructor_migration_target(ip="")


def test_migration_target_constructor_and_dict():
    target = constructor_migration_target()

    target_dict = target.to_dict()
    target2 = MigrationTarget.from_dict(target_dict)

    assert target.id == target2.id
    assert target2.cloud_type == CloudType.AWS


# Test dataclass Migration
def test_migration_error():
    with pytest.raises(BusinessRuleError):
        Migration(
            selected_mount_points=[MountPoint("A:\\", 100)],
            source="",
            migration_target=constructor_migration_target(),
        )

    with pytest.raises(BusinessRuleError):
        Migration(
            selected_mount_points=[MountPoint("A:\\", 100)],
            source=constructor_workload(),
            migration_target="",
        )

    with pytest.raises(BusinessRuleError):
        Migration(
            selected_mount_points=[MountPoint("A:\\", 100)],
            source=constructor_workload(),
            migration_target=constructor_migration_target(),
        )


def test_migration_constructor():
    src = constructor_workload()
    target = constructor_migration_target()

    migration = Migration(
        selected_mount_points=[MountPoint("D:\\", 100)],
        source=src,
        migration_target=target,
    )

    assert migration.selected_mount_points[0] == MountPoint("D:\\", 100)
    assert migration.source == src


def test_migration_run_error():
    src_with_issue = constructor_workload()
    src_with_issue.storage.append(MountPoint("C:\\", 100))
    bad_mig = Migration(
        selected_mount_points=[src_with_issue.storage[-1]],
        source=src_with_issue,
        migration_target=constructor_migration_target(),
    )

    with pytest.raises(BusinessRuleError):
        bad_mig.run(min_to_sleep=0)


def test_migration_run():
    src = constructor_workload()
    target = constructor_migration_target()

    migration = Migration(
        selected_mount_points=[src.storage[0]],
        source=src,
        migration_target=target,
    )
    migration.run(min_to_sleep=0)

    assert migration.state == MigrationState.SUCCESS
    assert migration.migration_target.target_vm.credentials.username == src.credentials.username

    # Test: re-run
    with pytest.raises(BusinessRuleError):
        migration.run(min_to_sleep=0)
