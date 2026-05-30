# -*- coding: utf-8 -*-
"""z_validator.py - Thin re-export wrapper. Real implementation in zrm_consciousness.py."""

from nexus.scripts.zrm_consciousness import ZValidator, ZViolationError, ZRMConsciousness

__all__ = ["ZValidator", "ZViolationError", "ZRMConsciousness"]
