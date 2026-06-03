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

"""Test script for the shared HTTP client.

Validates core functionality of the `HttpClient` class against a
public test endpoint. Run this to verify the HTTP client is properly
configured after installation.

Usage:
    python test_http_client.py
"""

# /// script
# requires-python = ">=3.10"
# ///

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http_client import HttpClient

if __name__ == "__main__":
    client = HttpClient(base_url="https://httpbin.org", qps=1.0)
    try:
        resp = client.fetch_json("/get")
        print("HTTP Client: OK -", resp.get("url", "unknown")[:50])
    except Exception as e:
        print("HTTP Client: Error -", str(e)[:80])
