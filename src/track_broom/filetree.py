"""File system entry models for representing files and directories."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


class FileSystemEntry:
    """Base class for file system entries (files and directories)."""

    name: str
    parent: FileSystemDirectoryEntry | None

    def __init__(self, path: Path, parent: FileSystemDirectoryEntry | None = None):
        self._path = path
        self._stat = path.stat()
        self.name = path.name
        self.parent = parent

    @property
    def size(self) -> int:
        """Size in bytes."""
        return self._stat.st_size

    @property
    def last_modified(self) -> datetime:
        """Last modification time as timezone-aware datetime."""
        return datetime.fromtimestamp(self._stat.st_mtime, tz=timezone.utc)

    @property
    def path(self) -> Path:
        """Full path to the entry."""
        return self._path

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, size={self.size})"


class FileSystemFileEntry(FileSystemEntry):
    """Represents a file in the file system."""

    @property
    def extension(self) -> str:
        """File extension including the dot, or empty string if none."""
        return self._path.suffix.lower()


class FileSystemDirectoryEntry(FileSystemEntry):
    """Represents a directory in the file system."""

    def entries(self) -> list[FileSystemEntry]:
        """Return all direct children of this directory."""
        result = []
        for child_path in self._path.iterdir():
            if child_path.is_dir():
                result.append(FileSystemDirectoryEntry(child_path, self))
            else:
                result.append(FileSystemFileEntry(child_path, self))
        return result

    def children(self) -> list[FileSystemFileEntry]:
        """Return only file children of this directory."""
        return [e for e in self.entries() if isinstance(e, FileSystemFileEntry)]
