# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""UV package installer wrapper for OpenCode science skills.

Provides `UVInstaller` — a thin wrapper around the `uv` CLI for installing
Python packages into isolated environments. Supports checking uv availability,
installing packages with pip-compatible interface, and exporting installed
package lists.
"""

# /// script
# requires-python = ">=3.10"
# ///

from __future__ import annotations

import subprocess
import sys


class UVInstaller:
    """Wrapper for the `uv` Python package installer.

    Example:
        uv = UVInstaller()
        if uv.available:
            result = uv.install(["numpy", "pandas>=2.0"])
    """

    def __init__(self, uv_cmd: str = "uv"):
        self._uv_cmd = uv_cmd
        self._available = self._check_uv()

    def _check_uv(self) -> bool:
        try:
            result = subprocess.run(
                [self._uv_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @property
    def available(self) -> bool:
        return self._available

    @property
    def uv_command(self) -> str:
        return self._uv_cmd

    @property
    def version(self) -> str | None:
        if not self._available:
            return None
        try:
            result = subprocess.run(
                [self._uv_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip()
        except Exception:
            return None

    def install(
        self,
        packages: list[str],
        timeout: int = 120,
    ) -> dict:
        """Install Python packages using uv.

        Args:
            packages: List of package specifiers (e.g. ["numpy", "pandas>=2.0"]).
            timeout: Maximum execution time in seconds.

        Returns:
            Dict with status, output, and optional error info.
        """
        if not self._available:
            return {
                "status": "error",
                "message": "uv is not installed or not found on PATH",
            }

        if not packages:
            return {
                "status": "error",
                "message": "No packages specified",
            }

        try:
            result = subprocess.run(
                [self._uv_cmd, "pip", "install"] + packages,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return {
                "status": "ok" if result.returncode == 0 else "error",
                "output": result.stdout[:500] if result.stdout else "",
                "stderr": result.stderr[:500] if result.stderr else "",
                "return_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": f"Install timed out after {timeout}s",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)[:100],
            }

    def list_installed(self, timeout: int = 30) -> dict:
        """List currently installed packages via uv pip freeze.

        Args:
            timeout: Maximum execution time in seconds.

        Returns:
            Dict with status and list of installed package strings.
        """
        if not self._available:
            return {
                "status": "error",
                "message": "uv is not installed or not found on PATH",
            }

        try:
            result = subprocess.run(
                [self._uv_cmd, "pip", "freeze"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            packages = [
                line.strip()
                for line in result.stdout.splitlines()
                if line.strip() and not line.startswith("#")
            ]

            return {
                "status": "ok",
                "packages": packages,
                "count": len(packages),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)[:100],
            }


if __name__ == "__main__":
    uv = UVInstaller()
    print(f"UV: {'Available' if uv.available else 'Not found'}")
    if uv.available and uv.version:
        print(f"Version: {uv.version}")
