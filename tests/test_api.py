"""
Test REST API.
Run server first, then:
    python tests/test_api.py
"""

import sys
import requests

API_URL = "http://127.0.0.1:8000"
REQ_TIMEOUT = 5


def create_workload(ip="10.0.0.1"):
    obj = {
        "ip": ip,
        "credentials": {"username": "user", "password": "pass", "domain": "dom"},
        "storage": [{"name": "D:\\\\", "total_size": 100}]
    }
    resp = requests.post(f"{API_URL}/workloads/", json=obj, timeout=REQ_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def try_change_ip(workload):
    wid = workload["id"]
    wrong_data = workload.copy()
    wrong_data["ip"] = "9.9.9.9"
    resp = requests.put(f"{API_URL}/workloads/{wid}", json=wrong_data, timeout=REQ_TIMEOUT)
    return resp


def creat_migration_target():
    data = {
        "cloud_type": "VCLOUD",
        "cloud_credentials": {"username": "u_c", "password": "p_c", "domain": "d_c"},
        "target_vm": {
            "ip": "10.0.0.2",
            "credentials": {"username": "user", "password": "pass", "domain": "dom"},
            "storage": []
        }
    }
    resp = requests.post(f"{API_URL}/migration_targets/", json=data, timeout=REQ_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def creat_migration(source, target):
    data = {
        "selected_mount_points": [{"name": "D:\\\\", "total_size": 100}],
        "source": source,
        "migration_target": target
    }
    resp = requests.post(f"{API_URL}/migrations/", json=data, timeout=REQ_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def run_migration(mid):
    return requests.post(f"{API_URL}/migrations/{mid}/run", timeout=REQ_TIMEOUT)


def check_migration(mid):
    # check status
    resp = requests.get(f"{API_URL}/migrations/{mid}/status", timeout=REQ_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def main():
    # 1) create workload
    wl = create_workload("10.0.0.1")
    print("Created workload:", wl)

    # 2) try change ip (should error)
    resp = try_change_ip(wl)
    print("Try change IP:", resp.status_code)
    if resp.ok:
        print("ERROR: IP was changed but should not!", resp.text)
        sys.exit(1)

    # 3) create target
    target = creat_migration_target()
    print("Created target:", target)

    # 4) create migration
    mig = creat_migration(wl, target)
    print("Created migration:", mig)

    # 5) run migration
    run_resp = run_migration(mig["id"])
    print("Run migration:", run_resp.status_code, run_resp.text)
    if not run_resp.ok:
        print("Run failed:", run_resp.text)
        sys.exit(2)

    # 6) check migration status
    status = check_migration(mig["id"])
    print("Migration status:", status)

    return 0


if __name__ == "__main__":
    sys.exit(main())
