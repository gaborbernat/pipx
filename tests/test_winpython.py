import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Final
from urllib.request import urlopen

import pytest

from pipx.constants import WINDOWS

_WINPYTHON_SHA256: Final[str] = "50438ca67201125b4be2c278741864b2d40aaeb403849b7abd1805c819e89473"
_WINPYTHON_URL: Final[str] = (
    "https://github.com/winpython/winpython/releases/download/7.1.20240203final/Winpython64-3.12.2.0dot.exe"
)


@pytest.mark.skipif(not WINDOWS, reason="requires the reported WinPython release")
def test_scoop_wrapper_from_winpython_scripts(tmp_path: Path) -> None:
    archive = tmp_path / "winpython.exe"
    with urlopen(_WINPYTHON_URL, timeout=60) as response, archive.open("wb") as file_handle:
        shutil.copyfileobj(response, file_handle)
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == _WINPYTHON_SHA256

    subprocess.run(["tar", "-xf", archive], cwd=tmp_path, check=True)
    root = tmp_path / "WPy64-31220"
    scripts = root / "scripts"
    scoop_wrapper = tmp_path / "scoop" / "pipx.bat"
    scoop_wrapper.parent.mkdir()
    scoop_wrapper.write_text("@python --version\n", encoding="utf-8")

    driver = tmp_path / "driver.bat"

    def run(command: str) -> subprocess.CompletedProcess[str]:
        driver.write_text(
            f'@echo off\ncall "{scripts / "env_for_icons.bat"}"\ncd /d "{scripts}"\n{command}\n',
            encoding="utf-8",
        )
        return subprocess.run(["cmd.exe", "/d", "/c", driver], capture_output=True, text=True, check=False)

    direct = run(f'"{root / "python-3.12.2.amd64" / "python.exe"}" --version')
    wrapped = run(f'call "{scoop_wrapper}"')

    expected = (0, "Python 3.12.2\n", "")
    actual = (
        (direct.returncode, direct.stdout, direct.stderr),
        (wrapped.returncode, wrapped.stdout, wrapped.stderr),
    )
    if actual != (expected, expected):
        raise AssertionError(json.dumps(actual))
