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
ADMXNavigator — pure tree navigation over parsed ADMX data.
"""

import logging
from typing import Any, Optional, Union

logger = logging.getLogger('gpuiservice')


class ADMXNavigator:
    """Pure tree navigation over ADMX data without I/O or worker dependencies."""

    SLASH_CATEGORIES = {"CD/DVD Applications", "Приложения для CD/DVD"}

    def __init__(self, data=None):
        self.data = data or {}

    def _find_category_with_slash(self, categories, parts, start_index):
        """
        Find category considering slash categories exceptions.

        Args:
            categories: List of categories to search
            parts: All path parts
            start_index: Starting index in parts

        Returns:
            tuple: (found_category, parts_used_count) or (None, 0)
        """
        part = parts[start_index]

        # 1. Direct search by current part
        for cat in categories:
            if isinstance(cat, dict) and cat.get("category") == part:
                return cat, 1

        # 2. Check slash categories
        for slash_cat in self.SLASH_CATEGORIES:
            if slash_cat.startswith(part + "/"):
                slash_parts = slash_cat.split("/")
                # Check if we have enough parts for full match
                if start_index + len(slash_parts) <= len(parts):
                    # Verify all parts match
                    if all(parts[start_index + j] == slash_parts[j] for j in range(len(slash_parts))):
                        # Find category by full name
                        for cat in categories:
                            if isinstance(cat, dict) and cat.get("category") == slash_cat:
                                return cat, len(slash_parts)
        return None, 0

    def _navigate_path(self, path: str) -> tuple[Any, list[str], bool]:
        """
        Navigate to path in data structure.

        Common navigation logic for get() and list_children().

        Args:
            path: Path to navigate (e.g., "Machine/categories/System")

        Returns:
            Tuple of (current_node, remaining_parts, found):
            - current_node: The node found at path (or None if not found)
            - remaining_parts: Parts of path not yet navigated
            - found: True if navigation succeeded to some point
        """
        if not path or path == "/":
            return self.data, [], True

        parts = path.strip("/").split("/")
        current = self.data
        i = 0

        while i < len(parts):
            part = parts[i]

            if isinstance(current, dict):
                if "category" in current:
                    result = self._navigate_category_node(current, parts, i)
                    if result is None:
                        return None, [], False
                    current, i = result
                    continue

                if part not in current:
                    # Check if this might be a policy lookup by displayName
                    # Return current node and remaining parts for get() to handle
                    return current, parts[i:], True
                current = current[part]
                i += 1
                continue

            if isinstance(current, list):
                found, parts_used = self._find_category_with_slash(current, parts, i)
                if not found:
                    return None, [], False
                current = found
                i += parts_used
                continue

            return None, [], False

        return current, parts[i:], True

    def _navigate_category_node(self, current: dict, parts: list[str], i: int) -> Optional[tuple[Any, int]]:
        """
        Navigate within a category node.

        Args:
            current: Current category node (dict with "category" key)
            parts: All path parts
            i: Current index in parts

        Returns:
            Tuple (new_current, new_index) or None if navigation failed
        """
        part = parts[i]

        if part == "policies":
            return current.get("policies"), i + 1

        if part == "inherited":
            inherited_list = current.get("inherited", [])
            return inherited_list, i + 1

        inherited_list = current.get("inherited", [])
        found_inherited, parts_used = self._find_category_with_slash(inherited_list, parts, i)
        if found_inherited:
            return found_inherited, i + parts_used

        if part in current:
            return current[part], i + 1

        return None

    def _format_children(self, current: Any, parent_path: str) -> list[Union[str, dict]]:
        """
        Format children of current node for list_children output.

        Args:
            current: Current node to format children for
            parent_path: Original parent path (for context)

        Returns:
            List of formatted children.
        """
        if isinstance(current, list):
            return [
                {"name": item.get("category", ""), "help": item.get("help", "")}
                for item in current
                if isinstance(item, dict) and "category" in item
            ]

        if isinstance(current, dict):
            is_category = ("category" in current) or ("inherited" in current) or ("policies" in current)

            if is_category:
                return list(current.keys())

            if parent_path.endswith("uncategorizedPolicies"):
                return [
                    {"name": policy.get("displayName", policy_id), "help": policy.get("help", "")}
                    for policy_id, policy in current.items()
                    if isinstance(policy, dict)
                ]

            if parent_path.endswith("policies"):
                return [
                    {"name": policy.get("displayName", policy_id), "help": policy.get("help", "")}
                    for policy_id, policy in current.items()
                    if isinstance(policy, dict)
                ]

            return list(current.keys())

        return []
