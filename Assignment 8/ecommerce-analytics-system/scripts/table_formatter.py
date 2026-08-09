"""Optional tabular formatting with a dependency-free fallback."""

from __future__ import annotations

from typing import Any

try:
    from tabulate import tabulate as _tabulate
except ModuleNotFoundError:
    _tabulate = None


def format_table(data: Any, **kwargs: Any) -> str:
    """Format tabular data, using tabulate when installed."""
    if _tabulate is not None:
        return _tabulate(data, **kwargs)
    if hasattr(data, "to_string"):
        return data.to_string(index=kwargs.get("showindex", False))
    return str(data)
