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

"""Workflow skill creator for OpenCode science skills.

Generates new skill templates from existing patterns. Produces SKILL.md
frontmatter and Python script scaffolds consistent with the ecosystem
conventions established across 37 science skills.
"""

# /// script
# requires-python = ">=3.10"
# ///

from __future__ import annotations

import os
import json
from datetime import datetime, timezone


SKILL_TEMPLATE = """---
name: {name}
version: "1.0.0"
kind: python
category: science
---
# {title}

{description}

## Prerequisites
- Dependencies: science_skills_common

## Usage
```python
from skills.science.{name}.scripts.{script_name} import {class_name}
```

## Configuration
- API base URL: `{api_url}`
- Rate limit: `{qps}` queries per second

## License
```
Copyright 2026 Google LLC
Licensed under the Apache License, Version 2.0
```
"""

SCRIPT_TEMPLATE = '''# Copyright 2026 Google LLC
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

"""{description}"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "science-skills-common",
# ]
# [tool.uv.sources]
# science-skills-common = {{ path = "../../science_skills_common" }}
# ///

from __future__ import annotations

from science_skills.science_skills_common import http_client


class {class_name}:
    """Client for the {api_name} API.

    Example:
        client = {class_name}()
        result = client.search("query")
    """

    BASE_URL = "{api_url}"

    def __init__(self, qps: float = {qps}):
        self._client = http_client.HttpClient(
            self.BASE_URL,
            qps=qps,
            referer_skill="{name}",
        )

    def fetch(self, endpoint: str) -> dict:
        resp = self._client.fetch_json(endpoint)
        return resp


if __name__ == "__main__":
    client = {class_name}()
    print(f"{{client.__class__.__name__}}: initialized")
'''


class SkillGenerator:
    """Generates templated science skill scaffolds.

    Example:
        gen = SkillGenerator()
        result = gen.generate(
            name="my_skill",
            title="My Skill",
            description="A new science skill.",
            class_name="MyClient",
            script_name="my_script.py",
            api_url="https://api.example.com",
            api_name="Example API",
        )
    """

    def __init__(self):
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def generate(
        self,
        name: str,
        title: str,
        description: str,
        class_name: str,
        script_name: str,
        api_url: str = "https://api.example.com",
        api_name: str = "Example API",
        qps: float = 3.0,
    ) -> dict:
        """Generate a new skill template with SKILL.md and Python script.

        Args:
            name: Skill directory name (snake_case).
            title: Human-readable skill title.
            description: Short description of the skill.
            class_name: Python class name for the client.
            script_name: Python script filename.
            api_url: Base URL of the target API.
            api_name: Human-readable API name.
            qps: Default queries per second rate limit.

        Returns:
            Dict with skill name, SKILL.md template, script template,
            and generation timestamp.
        """
        skill_md = SKILL_TEMPLATE.format(
            name=name,
            title=title,
            description=description,
            class_name=class_name,
            script_name=script_name,
            api_url=api_url,
            qps=qps,
        )

        script_py = SCRIPT_TEMPLATE.format(
            description=description,
            class_name=class_name,
            api_name=api_name,
            api_url=api_url,
            qps=qps,
            name=name,
        )

        return {
            "status": "generated",
            "skill_name": name,
            "skill_md": skill_md,
            "script_py": script_py,
            "class_name": class_name,
            "script_name": script_name,
            "api_url": api_url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def save_to_disk(
        self,
        base_path: str,
        result: dict,
    ) -> dict:
        """Write the generated skill to disk.

        Args:
            base_path: Root directory to create the skill under.
            result: Dict returned by `generate()`.

        Returns:
            Dict with paths of created files.
        """
        skill_dir = os.path.join(base_path, result["skill_name"])
        scripts_dir = os.path.join(skill_dir, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)

        skill_md_path = os.path.join(skill_dir, "SKILL.md")
        script_py_path = os.path.join(
            scripts_dir,
            result["script_name"],
        )

        with open(skill_md_path, "w", encoding="utf-8") as f:
            f.write(result["skill_md"])

        with open(script_py_path, "w", encoding="utf-8") as f:
            f.write(result["script_py"])

        return {
            "status": "saved",
            "skill_dir": skill_dir,
            "skill_md": skill_md_path,
            "script_py": script_py_path,
        }


if __name__ == "__main__":
    gen = SkillGenerator()
    print(f"SkillGenerator: {'Available' if gen.available else 'Error'}")

    r = gen.generate(
        name="test_skill",
        title="Test Skill",
        description="A test skill for validation.",
        class_name="TestClient",
        script_name="test.py",
        api_url="https://httpbin.org",
        api_name="HTTPBin Test API",
    )
    print(f"Generate: {r['status']}")
    print(f"Timestamp: {r['timestamp']}")
