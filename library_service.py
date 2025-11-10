"""
Compatibility shim for tests that import `library_service` at the top-level.

Some tests import `library_service` (top-level) while others import
`services.library_service`. To support both without changing tests, re-export
the symbols from `services.library_service`.
"""

from services.library_service import *  # re-export everything for tests

__all__ = [name for name in dir() if not name.startswith("_")]
