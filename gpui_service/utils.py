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


def resolve_gpo_path(path, sysvol_path):
    """
    Resolve UNC or absolute GPO path to relative path within sysvol.
    """
    if isinstance(path, str):
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


def normalize_path_separators(path):
    """Normalize path separators to forward slashes."""
    return path.replace('\\', '/')


def is_unc_path(path):
    """Check if path is a UNC path."""
    return isinstance(path, str) and path.startswith('\\\\')
