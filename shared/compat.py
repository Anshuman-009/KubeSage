"""Python version compatibility helpers."""

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """Backport of enum.StrEnum for Python < 3.11."""

        pass

__all__ = ["StrEnum"]
