"""Domain-level semantic types and identifiers."""

from typing import NewType

TrackId = NewType("TrackId", int)
ExternalTrackId = NewType("ExternalTrackId", str)

__all__ = [
    "ExternalTrackId",
    "TrackId",
]
