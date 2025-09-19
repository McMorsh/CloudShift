import json
import os
from pathlib import Path
from typing import Any


# Safe write(os.replace)
def write_json(path: Path, obj: dict[str, Any]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)

    os.replace(tmp_path, path)


def read_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
