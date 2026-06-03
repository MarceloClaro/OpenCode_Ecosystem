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

"""PyMOL headless renderer for OpenCode Ecosystem.

Generates molecular visualization images without GUI.
Supports PDB structures with cartoon, surface, and stick representations.
"""

# /// script
# requires-python = ">=3.10"
# ///

from __future__ import annotations

import os
import subprocess
import tempfile

DEFAULT_WIDTH = 1200
DEFAULT_HEIGHT = 800
DEFAULT_DPI = 300


class PyMOLRenderer:
    """Headless PyMOL renderer for protein structure visualization.

    Example:
        renderer = PyMOLRenderer()
        if renderer.available:
            result = renderer.render("4hhb.pdb", output="4hhb.png")
    """

    def __init__(self, pymol_cmd: str = "pymol"):
        self._pymol_cmd = pymol_cmd
        self._available = self._check_pymol()

    def _check_pymol(self) -> bool:
        try:
            result = subprocess.run(
                [self._pymol_cmd, "-cq"],
                capture_output=True,
                timeout=5,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @property
    def available(self) -> bool:
        return self._available

    @property
    def pymol_command(self) -> str:
        return self._pymol_cmd

    def render(
        self,
        pdb_file: str,
        output: str | None = None,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        dpi: int = DEFAULT_DPI,
        representation: str = "cartoon",
        color_scheme: str = "chain",
        background: str = "white",
        ray_trace: bool = True,
    ) -> dict:
        """Render a PDB structure to PNG.

        Args:
            pdb_file: Path to PDB structure file.
            output: Output PNG path (default: temp directory).
            width: Image width in pixels.
            height: Image height in pixels.
            dpi: Rendering DPI for ray tracing.
            representation: PyMOL representation (cartoon, surface, sticks, ribbon).
            color_scheme: PyMOL color command (chain, spectrum, ss, atomic).
            background: Background color.
            ray_trace: Whether to ray trace (higher quality, slower).

        Returns:
            Dict with status, output file path, and optional error info.
        """
        if not self._available:
            return {
                "status": "error",
                "message": "PyMOL is not installed or not found on PATH",
                "file": None,
            }

        if not os.path.isfile(pdb_file):
            return {
                "status": "error",
                "message": f"PDB file not found: {pdb_file}",
                "file": None,
            }

        if not output:
            basename = os.path.splitext(os.path.basename(pdb_file))[0]
            output = os.path.join(
                tempfile.gettempdir(),
                f"pymol_{basename}.png",
            )

        output = os.path.abspath(output)
        os.makedirs(os.path.dirname(output), exist_ok=True)

        script_content = f"""
load {pdb_file}
bg {background}
show {representation}
color {color_scheme}
set ray_opaque_background, off
set antialias, 2
"""

        if ray_trace:
            script_content += f"""
set ray_trace_mode, 3
ray {width},{height}
"""

        script_content += f"""
png {output}, dpi={dpi}
quit
"""

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".pml",
                delete=False,
                encoding="utf-8",
            ) as script_file:
                script_file.write(script_content)
                script_path = script_file.name

            result = subprocess.run(
                [self._pymol_cmd, "-cq", script_path],
                capture_output=True,
                text=True,
                timeout=120,
            )

            os.unlink(script_path)

            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": result.stderr.strip()[:200],
                    "file": output,
                }

            if os.path.isfile(output):
                return {
                    "status": "ok",
                    "file": output,
                    "size_bytes": os.path.getsize(output),
                }

            return {
                "status": "error",
                "message": "Render completed but output file not found",
                "file": output,
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "PyMOL render timed out (120s)",
                "file": output,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)[:200],
                "file": output,
            }


if __name__ == "__main__":
    renderer = PyMOLRenderer()
    print(f"PyMOL Renderer: {'Available' if renderer.available else 'Not found'}")
