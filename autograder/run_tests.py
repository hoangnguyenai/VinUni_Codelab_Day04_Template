"""Run all lab tests with isolated JSON data (no test tickets in raw-data)."""

from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if (ROOT / ".lab-deps").is_dir():
    sys.path.insert(0, str(ROOT / ".lab-deps"))
sys.path.insert(0, str(ROOT / "starter-code"))

import pytest
import tools


def main():
    original_data_dir = tools.RAW_DATA_DIR
    with tempfile.TemporaryDirectory(prefix="vinassistant-tests-") as temporary:
        data_dir = Path(temporary) / "raw-data"
        shutil.copytree(ROOT / "raw-data", data_dir)
        tools.RAW_DATA_DIR = str(data_dir)
        try:
            return pytest.main([
                str(ROOT / "autograder" / "test_agent.py"),
                str(ROOT / "autograder" / "test_edge_cases.py"),
                "--basetemp", str(Path(temporary) / "pytest"),
                "-v", "--tb=short",
            ])
        finally:
            tools.RAW_DATA_DIR = original_data_dir


if __name__ == "__main__":
    raise SystemExit(main())
