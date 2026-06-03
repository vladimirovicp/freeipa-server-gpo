#
# gpuiservice - GPT Directory Management API Service
#
# Copyright (C) 2025-2026 BaseALT Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Utility functions for path resolution and normalization.
"""

import os
import tempfile
from pathlib import Path


def resolve_gpo_path(path: str | None, sysvol_path: str) -> str:
    """
    Resolve UNC or absolute GPO path to relative path within sysvol.

    Args:
        path: GPO path (UNC, absolute, or relative)
        sysvol_path: Base sysvol path for resolution

    Returns:
        Resolved relative path within sysvol.
    """
    if isinstance(path, str):
        if path.startswith('\\') and not path.startswith('\\\\'):
            path = '\\' + path

        if path.startswith('\\\\'):
            parts = path.split('\\')
            local_parts = parts[4:]
            if len(parts) >= 5 and local_parts:
                return '/'.join([p for p in local_parts if p]).rstrip('/')
            else:
                return path.replace('\\', '/').rstrip('/')

        if path.startswith(sysvol_path):
            rel_path = path[len(sysvol_path):].lstrip('/')
            return rel_path.replace('\\', '/').rstrip('/')
        return path.replace('\\', '/').rstrip('/')

    return str(path)


def normalize_path_separators(path: str) -> str:
    """
    Normalize path separators to forward slashes.

    Args:
        path: Path with potential backslashes

    Returns:
        Path with forward slashes only.
    """
    return path.replace('\\', '/')


def is_unc_path(path: str | None) -> bool:
    """
    Check if path is a UNC path.

    Args:
        path: Path to check

    Returns:
        True if path is a UNC path (starts with \\\\), False otherwise.
    """
    return isinstance(path, str) and path.startswith('\\\\')


def validate_path_in_sysvol(resolved_path: str, sysvol_path: str) -> None:
    """
    Validate that resolved_path does not escape sysvol_path via path traversal.

    Args:
        resolved_path: Path to validate (must be already resolved/joined)
        sysvol_path: Base sysvol path

    Raises:
        ValueError: If path traversal is detected
    """
    from pathlib import Path
    real_sysvol = Path(sysvol_path).resolve()
    real_path = Path(resolved_path).resolve()
    sysvol_str = str(real_sysvol)
    path_str = str(real_path)
    if path_str != sysvol_str and not path_str.startswith(sysvol_str + '/'):
        raise ValueError("Path traversal detected: {} escapes {}".format(resolved_path, sysvol_path))


def atomic_write(path, content, encoding='utf-8', suffix='.tmp'):
    """Write content to file atomically via temp file + os.replace.

    Args:
        path: Target file path.
        content: String content to write.
        encoding: Text encoding (default utf-8).
        suffix: Temp file suffix.
    """
    dir_path = os.path.dirname(path)
    os.makedirs(dir_path, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(suffix=suffix, dir=dir_path)
    try:
        with os.fdopen(fd, 'w', encoding=encoding) as f:
            f.write(content)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def atomic_write_bytes(path, content, suffix='.tmp'):
    """Write bytes content to file atomically via temp file + os.replace.

    Args:
        path: Target file path.
        content: Bytes content to write.
        suffix: Temp file suffix.
    """
    dir_path = os.path.dirname(path)
    os.makedirs(dir_path, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(suffix=suffix, dir=dir_path)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(content)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise
