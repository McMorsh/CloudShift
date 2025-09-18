import time
from uuid import uuid4
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Any

from .exceptions import BusinessRuleError


@dataclass(frozen=True)
class Credentials:
    """
    Authentication data for a workload and cloud target

    Attributes:
        username (str): Login, should not be None
        password (str): Password, should not be None
        domain (str): Domain
    """
    username: str
    password: str
    domain: str

    def __post_init__(self):
        """
        :raise BusinessRuleError: If username or password are None
        """
        if not self.username or not self.password:
            raise BusinessRuleError("username, password are required")


@dataclass(frozen=True)
class MountPoint:
    """
    Represents of VM

    Attributes:
        name (str):  Mount point name (for example, "C:\\")
        total_size (int): Total size of the volume (int)
    """
    name: str
    total_size: int

    def __post_init__(self):
        """
        :raise BusinessRuleError: If name is None or size < 0
        """
        if not self.name:
            raise BusinessRuleError("name is required")
        if self.total_size < 0:
            raise BusinessRuleError("total_size cannot be negative")


@dataclass
class Workload:
    """
    Represents source of VM

    Attributes:
        ip (str): IP address of VM
        credentials (Credentials): Authentication data
        storage (List(MountPoint)): List of disk
        id (str): Workload ID
    """
    ip: str
    credentials: Credentials
    storage: List[MountPoint]
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        """
        raises BusinessRuleError: If ip is required or credentials is wrong type
        """
        if not self.ip or self.ip == "":
            raise BusinessRuleError("ip is required")
        if not isinstance(self.credentials, Credentials):
            raise BusinessRuleError("credentials should be a Credentials")

    def to_dict(self) -> dict[str, Any]:
        return {
            "ip": self.ip,
            "credentials": asdict(self.credentials),
            "storage": [asdict(mp) for mp in self.storage],
            "id": self.id
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Workload":
        credentials_data = Credentials(**data["credentials"])
        storage_data = [MountPoint(**mp) for mp in data["storage"]]
        if "id" in data and data["id"] is not None:
            return cls(ip=data["ip"], credentials=credentials_data, storage=storage_data, id=data["id"])
        else:
            return cls(ip=data["ip"], credentials=credentials_data, storage=storage_data)


class CloudType(Enum):
    AWS = "AWS"
    AZURE = "AZURE"
    VSPHERE = "VSPHERE"
    VCLOUD = "VCLOUD"


@dataclass
class MigrationTarget:
    """
    Represents of a place for migration

    Attributes:
        cloud_type (CloudType): Cloud type to use
        cloud_credentials (Credentials): Authentication data
        target_vm (Workload): The vm that will become the migration target
        id (str): MigrationTarget ID
    """
    cloud_type: CloudType
    cloud_credentials: Credentials
    target_vm: Workload
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        """
        :raises BusinessRuleError:  If cloud_type or credentials or target_vm is wrong type
        """
        if not isinstance(self.cloud_type, CloudType):
            raise BusinessRuleError("cloud_type should be a CloudType")
        if not isinstance(self.cloud_credentials, Credentials):
            raise BusinessRuleError("cloud_credentials should be a Credentials")
        if not isinstance(self.target_vm, Workload):
            raise BusinessRuleError("target_vm should be a Workload")

    def to_dict(self) -> dict[str, Any]:
        return {
            "cloud_type": self.cloud_type.value,
            "cloud_credentials": asdict(self.cloud_credentials),
            "target_vm": self.target_vm.to_dict(),
            "id": self.id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MigrationTarget":
        credentials_data = Credentials(**data["cloud_credentials"])
        if "id" in data and data["id"] is not None:
            return cls(cloud_type=CloudType(data["cloud_type"]), cloud_credentials=credentials_data, target_vm=Workload.from_dict(data["target_vm"]), id=data["id"])
        else:
            return cls(cloud_type=CloudType(data["cloud_type"]), cloud_credentials=credentials_data, target_vm=Workload.from_dict(data["target_vm"]))


class MigrationState(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


@dataclass
class Migration:
    """
    Represents a migration process

    Attributes:
        selected_mount_points (List[MountPoint]): List of selected mount points(disks)
        source (Workload): Source of VM
        migration_target (MigrationTarget): Migration target
        state (MigrationState): Current state of migration
        id (str): Migration ID
    """
    selected_mount_points: list[MountPoint]
    source: Workload
    migration_target: MigrationTarget
    state: MigrationState = field(default=MigrationState.NOT_STARTED)
    id: str = field(default=str(uuid4()))

    def __post_init__(self):
        if not isinstance(self.source, Workload):
            raise BusinessRuleError("source should be a Workload")
        if not isinstance(self.migration_target, MigrationTarget):
            raise BusinessRuleError("migration_target should be a MigrationTarget")

        # Check that the selected mount point exist in the storage
        source_names = {mp.name for mp in self.source.storage}
        for mp in self.selected_mount_points:
            if mp.name not in source_names:
                raise BusinessRuleError(f"selected mount point {mp.name} is not a storage mount point")

    def run(self, min_to_sleep: int = 1) -> None:
        """
        Execute the migration

        :param min_to_sleep: Number of minutes to sleep before executing migration
        :return: None

        :raises BusinessRuleError: IF wrong state or migrations is running when volume 'C:\\'
        """
        if self.state not in (MigrationState.NOT_STARTED, MigrationState.ERROR):
            raise BusinessRuleError("Migration already started or completed")

        # Business logic: migrations is not allowed running when volume C:\
        for mp in self.selected_mount_points:
            normalized = mp.name.strip().rstrip("/\\").lower()
            if normalized == "c:":
                self.state = MigrationState.ERROR
                raise BusinessRuleError("migrations is not allowed running when volume 'C:\\'")

        self.state = MigrationState.RUNNING

        # Simulate running migration
        time.sleep(60 * min_to_sleep)

        # Business logic: target should only have mount points that are selected
        selected_names = {mp.name for mp in self.selected_mount_points}
        filtered_storage = [mp for mp in self.source.storage if mp.name in selected_names]

        # Copy data
        target = self.migration_target.target_vm
        target.credentials = self.source.credentials
        target.storage = filtered_storage

        self.state = MigrationState.SUCCESS

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_mount_points": [asdict(mp) for mp in self.selected_mount_points],
            "source": self.source.to_dict(),
            "migration_target": self.migration_target.to_dict(),
            "state": self.state.value,
            "id": self.id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Migration":
        storage_data = [MountPoint(**mp) for mp in data["selected_mount_points"]]
        if "id" in data and data["id"] is not None:
            return cls(selected_mount_points=storage_data,
            source=Workload.from_dict(data["source"]),
            migration_target=MigrationTarget.from_dict(data["migration_target"]),
            state=MigrationState(data.get("state", MigrationState.NOT_STARTED.value)), id=data["id"])
        else:
            return cls(selected_mount_points=storage_data,
            source=Workload.from_dict(data["source"]),
            migration_target=MigrationTarget.from_dict(data["migration_target"]),
            state=MigrationState(data.get("state", MigrationState.NOT_STARTED.value)))
