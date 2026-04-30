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
GPTWorker - Worker for GPT policy file (.pol) creation and parsing
Uses Samba GPPolParser for reading/writing Group Policy registry.pol files
"""

import logging
from pathlib import Path
import traceback

try:
    from . import utils
    from .config import DEFAULT_SYSVOL_PATH
except ImportError:
    import utils
    from config import DEFAULT_SYSVOL_PATH

logger = logging.getLogger('gpuiservice')

class GPTWorker:
    """
    Worker for GPT policy file (.pol) creation and parsing

    This class provides functionality to create and parse Group Policy
    registry.pol files using Samba's GPPolParser. It integrates with
    GPODataStore to enable writing policy values to GPT structures.

    Typical usage:
        worker = GPTWorker(sysvol_path='/var/lib/freeipa/sysvol')
        worker.update_policy_value(
            gpo_path='domain.example.com/Policies/{GUID}',
            key='Software\\BaseALT\\Policies\\SomePolicy',
            value_name='SomeValue',
            value_data=1,
            value_type='REG_DWORD'
        )
    """

    def __init__(self, sysvol_path=DEFAULT_SYSVOL_PATH):
        """
        Initialize GPT policy worker

        Args:
            sysvol_path: Path to FreeIPA sysvol directory where GPT structures are stored
        """
        self.sysvol_path = Path(sysvol_path)
        self.pol_parser = None

        # Try to import Samba GPPolParser
        try:
            from samba.gp_parse.gp_pol import GPPolParser
            from samba.dcerpc import misc, preg
            self.pol_parser = GPPolParser
            self.preg = preg
            self.reg_constants = misc
            # Build registry type mapping
            self.reg_type_map = {
                'REG_SZ': misc.REG_SZ,
                'REG_EXPAND_SZ': misc.REG_EXPAND_SZ,
                'REG_BINARY': misc.REG_BINARY,
                'REG_DWORD': misc.REG_DWORD,
                'REG_DWORD_BIG_ENDIAN': misc.REG_DWORD_BIG_ENDIAN,
                'REG_LINK': misc.REG_LINK,
                'REG_MULTI_SZ': misc.REG_MULTI_SZ,
                'REG_QWORD': misc.REG_QWORD,
                'REG_NONE': misc.REG_NONE,
            }
            # Add additional registry types if available in Samba
            for reg_name in ['REG_RESOURCE_LIST', 'REG_FULL_RESOURCE_DESCRIPTOR', 'REG_RESOURCE_REQUIREMENTS_LIST']:
                if hasattr(misc, reg_name):
                    self.reg_type_map[reg_name] = getattr(misc, reg_name)
            self.reg_type_reverse = {v: k for k, v in self.reg_type_map.items()}
            logger.debug("Samba GPPolParser imported successfully")
        except ImportError as exp:
            logger.warning(f"Samba GPPolParser not available: {exp}")
            logger.warning("GPT policy file operations will be limited")

    def _get_pol_file_path(self, gpo_path, policy_type='Machine'):
        """
        Get the path to registry.pol file for a given GPO

        Args:
            gpo_path: Relative path to GPO within sysvol (e.g., 'domain/Policies/{GUID}')
            policy_type: 'Machine' or 'User' policy file

        Returns:
            Path object to the registry.pol file

        Raises:
            ValueError: If path traversal is detected
        """
        gpo_full_path = self.sysvol_path / gpo_path
        utils.validate_path_in_sysvol(str(gpo_full_path), str(self.sysvol_path))
        if policy_type == 'Machine':
            return gpo_full_path / 'Machine' / 'Registry.pol'
        else:  # User
            return gpo_full_path / 'User' / 'Registry.pol'

    def _normalize_gpo_path(self, gpo_path, policy_type='Machine'):
        """
        Normalize GPO path argument to handle both GPO paths and .pol file paths

        This method allows callers to pass either:
        1. GPO path (relative to sysvol) + policy_type
        2. Full path to registry.pol file (policy_type inferred from parent directory)

        Args:
            gpo_path: Either GPO path (relative) or Path to registry.pol file
            policy_type: Default policy type if not inferred from path

        Returns:
            Tuple of (normalized_gpo_path, policy_type)
            normalized_gpo_path is relative GPO path (string) ready for _get_pol_file_path
        """
        # Convert to Path object if string
        path = Path(gpo_path) if isinstance(gpo_path, str) else gpo_path

        # Check if this looks like a registry.pol file path
        if path.name == 'Registry.pol':
            # Determine policy type from parent directory name
            parent = path.parent.name
            if parent in ('Machine', 'User'):
                policy_type = parent
                # Get GPO path relative to sysvol_path
                # path.parent.parent is the GPO directory (e.g., g1)
                try:
                    gpo_relative = path.parent.parent.relative_to(self.sysvol_path)
                    return str(gpo_relative), policy_type
                except ValueError:
                    # Path is not under sysvol_path, treat as absolute GPO path
                    # Return absolute path as string
                    abs_path = str(path.parent.parent)
                    resolved_path = utils.resolve_gpo_path(abs_path, str(self.sysvol_path))
                    return resolved_path, policy_type
            # If parent not Machine/User, fall through

        # Not a .pol file path, treat as GPO path
        # Convert to string if it's a Path
        if isinstance(gpo_path, Path):
            gpo_path = str(gpo_path)
        # Resolve UNC or absolute path to relative sysvol path
        gpo_path = utils.resolve_gpo_path(gpo_path, str(self.sysvol_path))
        return gpo_path, policy_type

    def create_pol_file(self, gpo_path, policy_type='Machine', policies=None):
        """
        Create a new registry.pol file with given policies

        Args:
            gpo_path: Relative path to GPO within sysvol
            policy_type: 'Machine' or 'User' policy file
            policies: Dictionary of policies to write, where key is registry path
                     and value is tuple (value_name, value_data, value_type)
                     Example: {
                         'Software\\BaseALT\\Policies\\GPUpdate':
                         ('SomeValue', 1, 'REG_DWORD')
                     }

        Returns:
            True if successful, False otherwise
        """
        if not self.pol_parser:
            logger.error("Cannot create .pol file: Samba GPPolParser not available")
            return False

        # Normalize GPO path (handles both GPO path and .pol file path)
        gpo_path, policy_type = self._normalize_gpo_path(gpo_path, policy_type)

        pol_file_path = self._get_pol_file_path(gpo_path, policy_type)

        try:
            # Ensure parent directory exists
            pol_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Create new GPPolParser instance
            parser = self.pol_parser()
            # Initialize pol_file with signature and version
            parser.pol_file = self.preg.file()
            parser.pol_file.header.signature = 'PReg'
            parser.pol_file.header.version = 1
            entries = []
            total_entries = 0

            if policies:
                for key_path, value_info in policies.items():
                    # Handle both nested dict format and legacy tuple format
                    if isinstance(value_info, dict):
                        # Nested dict format: {key_path: {value_name: (value_data, value_type)}}
                        for value_name, (value_data, value_type) in value_info.items():
                            samba_type = self._convert_to_samba_type(value_type)
                            entry = self.preg.entry()
                            entry.type = samba_type
                            entry.keyname = key_path
                            entry.valuename = value_name if value_name is not None else ''
                            entry.data = self._value_to_samba_data(value_data, samba_type)
                            entries.append(entry)
                            total_entries += 1
                    elif isinstance(value_info, tuple) and len(value_info) == 3:
                        # Legacy tuple format: (value_name, value_data, value_type)
                        value_name, value_data, value_type = value_info
                        samba_type = self._convert_to_samba_type(value_type)
                        entry = self.preg.entry()
                        entry.type = samba_type
                        entry.keyname = key_path
                        entry.valuename = value_name if value_name is not None else ''
                        entry.data = self._value_to_samba_data(value_data, samba_type)
                        entries.append(entry)
                        total_entries += 1
                    else:
                        logger.warning(f"Unexpected policy format for key {key_path}: {value_info}")
                        continue

            parser.pol_file.num_entries = total_entries
            parser.pol_file.entries = entries
            # Write binary file
            parser.write_binary(str(pol_file_path))

            logger.info(f"Created registry.pol file at {pol_file_path} with {total_entries} policies")
            return True

        except PermissionError as exp:
            logger.error(f"Permission denied writing to {pol_file_path}: {exp}")
            return False
        except (OSError, IOError) as exp:
            logger.error(f"I/O error writing registry.pol to {pol_file_path}: {exp}")
            return False
        except (ValueError, RuntimeError) as exp:
            logger.error(f"Data error creating registry.pol file at {pol_file_path}: {exp}")
            return False
        except Exception as exp:
            logger.exception(f"Unexpected error creating registry.pol file at {pol_file_path}: {exp}")
            return False

    def read_pol_file(self, gpo_path, policy_type='Machine'):
        """
        Read and parse a registry.pol file

        Args:
            gpo_path: Relative path to GPO within sysvol
            policy_type: 'Machine' or 'User' policy file

        Returns:
            Dictionary of policies where key is registry path and value is
            tuple (value_name, value_data, value_type), or empty dict if file doesn't exist
        """
        if not self.pol_parser:
            logger.error("Cannot read .pol file: Samba GPPolParser not available")
            return {}

        # Normalize GPO path (handles both GPO path and .pol file path)
        gpo_path, policy_type = self._normalize_gpo_path(gpo_path, policy_type)

        pol_file_path = self._get_pol_file_path(gpo_path, policy_type)

        if not pol_file_path.exists():
            logger.debug(f"registry.pol file not found at {pol_file_path}")
            return {}

        try:
            # Parse existing file
            parser = self.pol_parser()
            with open(pol_file_path, 'rb') as f:
                parser.parse(f.read())

            # Extract policies from pol_file entries
            policies = {}
            if parser.pol_file and parser.pol_file.entries:
                for entry in parser.pol_file.entries:
                    key_path = entry.keyname
                    value_name = entry.valuename
                    # Convert Samba data to Python value
                    value_data = self._samba_data_to_value(entry.data, entry.type)
                    value_type = self._convert_from_samba_type(entry.type)

                    # Store as nested dict: {key_path: {value_name: (value_data, value_type)}}
                    if key_path not in policies:
                        policies[key_path] = {}
                    policies[key_path][value_name] = (value_data, value_type)

            logger.debug(f"Read {len(policies)} policies from {pol_file_path}")
            return policies

        except PermissionError as exp:
            logger.error(f"Permission denied reading {pol_file_path}: {exp}")
            return {}
        except (OSError, IOError) as exp:
            logger.error(f"I/O error reading registry.pol from {pol_file_path}: {exp}")
            return {}
        except (ValueError, RuntimeError) as exp:
            logger.error(f"Data error reading registry.pol from {pol_file_path}: {exp}")
            return {}
        except Exception as exp:
            logger.exception(f"Unexpected error reading registry.pol file at {pol_file_path}: {exp}")
            return {}

    def update_policy_value(self, gpo_path, key_path, value_name, value_data,
                           value_type='REG_DWORD', policy_type='Machine'):
        """
        Update a single policy value in registry.pol file

        This method reads the existing file, updates or adds the specified policy,
        and writes the file back.

        Args:
            gpo_path: Relative path to GPO within sysvol
            key_path: Registry key path (e.g., 'Software\\BaseALT\\Policies\\GPUpdate')
            value_name: Name of the value to set
            value_data: Data to set (type depends on value_type)
            value_type: Registry value type ('REG_SZ', 'REG_DWORD', 'REG_QWORD', 'REG_BINARY', etc.)
            policy_type: 'Machine' or 'User' policy file

        Returns:
            True if successful, False otherwise
        """
        if not self.pol_parser:
            logger.error("Cannot update policy: Samba GPPolParser not available")
            return False

        # Normalize GPO path (handles both GPO path and .pol file path)
        gpo_path, policy_type = self._normalize_gpo_path(gpo_path, policy_type)
        pol_file_path = self._get_pol_file_path(gpo_path, policy_type)

        try:
            # Read existing policies (nested dict format)
            existing_policies = self.read_pol_file(gpo_path, policy_type)

            # Ensure key_path exists as dict
            if key_path not in existing_policies:
                existing_policies[key_path] = {}

            # Update or add the specific value name
            existing_policies[key_path][value_name] = (value_data, value_type)

            # Create/update the file (pass nested dict directly)
            return self.create_pol_file(gpo_path, policy_type, existing_policies)

        except (OSError, IOError) as exp:
            logger.error(f"I/O error updating policy in {pol_file_path}: {exp}")
            return False
        except (ValueError, RuntimeError) as exp:
            logger.error(f"Data error updating policy in {pol_file_path}: {exp}")
            return False
        except Exception as exp:
            logger.exception(f"Unexpected error updating policy value in {pol_file_path}: {exp}")
            return False

    def get_policy_value(self, gpo_path, key_path, value_name, policy_type='Machine'):
        """
        Get a specific policy value from registry.pol file

        Args:
            gpo_path: Relative path to GPO within sysvol
            key_path: Registry key path
            value_name: Name of the value to retrieve
            policy_type: 'Machine' or 'User' policy file

        Returns:
            Tuple of (value_data, value_type) if found, None otherwise
        """
        if not self.pol_parser:
            logger.error("Cannot get policy value: Samba GPPolParser not available")
            return None
        # Normalize GPO path (handles both GPO path and .pol file path)
        gpo_path, policy_type = self._normalize_gpo_path(gpo_path, policy_type)
        policies = self.read_pol_file(gpo_path, policy_type)

        if key_path in policies and value_name in policies[key_path]:
            v_data, v_type = policies[key_path][value_name]
            return v_data, v_type

        logger.debug(f"Policy value not found: {key_path}\\{value_name}")
        return None

    def delete_policy_value(self, gpo_path, key_path, value_name, policy_type='Machine'):
        """
        Delete a specific policy value from registry.pol file

        Args:
            gpo_path: Relative path to GPO within sysvol
            key_path: Registry key path
            value_name: Name of the value to delete
            policy_type: 'Machine' or 'User' policy file

        Returns:
            True if successful (or value didn't exist), False on error
        """
        if not self.pol_parser:
            logger.error("Cannot delete policy: Samba GPPolParser not available")
            return False

        # Normalize GPO path (handles both GPO path and .pol file path)
        gpo_path, policy_type = self._normalize_gpo_path(gpo_path, policy_type)
        pol_file_path = self._get_pol_file_path(gpo_path, policy_type)

        if not pol_file_path.exists():
            logger.debug(f"registry.pol file not found at {pol_file_path}")
            return True

        try:
            # Read existing policies (nested dict format)
            existing_policies = self.read_pol_file(gpo_path, policy_type)

            # Remove the specific value if it exists
            if key_path in existing_policies and value_name in existing_policies[key_path]:
                del existing_policies[key_path][value_name]
                # If key_path dict becomes empty, remove it
                if not existing_policies[key_path]:
                    del existing_policies[key_path]
            else:
                # Policy doesn't exist
                logger.debug(f"Policy value not found: {key_path}\\{value_name}")
                return True

            # Write updated file (or delete if empty)
            if existing_policies:
                return self.create_pol_file(gpo_path, policy_type, existing_policies)
            else:
                # Delete empty file
                pol_file_path.unlink()
                logger.info(f"Deleted empty registry.pol file at {pol_file_path}")
                return True

        except PermissionError as exp:
            logger.error(f"Permission denied deleting from {pol_file_path}: {exp}")
            return False
        except (OSError, IOError) as exp:
            logger.error(f"I/O error deleting policy from {pol_file_path}: {exp}")
            return False
        except (ValueError, RuntimeError) as exp:
            logger.error(f"Data error deleting policy from {pol_file_path}: {exp}")
            return False
        except Exception as exp:
            logger.exception(f"Unexpected error deleting policy value from {pol_file_path}: {exp}")
            return False

    def _convert_to_samba_type(self, reg_type):
        """
        Convert registry type string to Samba constant

        Args:
            reg_type: Registry type string ('REG_SZ', 'REG_DWORD', etc.)

        Returns:
            Samba constant for the registry type
        """
        if hasattr(self, 'reg_type_map'):
            return self.reg_type_map.get(reg_type, self.reg_constants.REG_SZ)
        # Fallback mapping if Samba not available
        fallback_map = {
            'REG_NONE': 0,
            'REG_SZ': 1,
            'REG_EXPAND_SZ': 2,
            'REG_BINARY': 3,
            'REG_DWORD': 4,
            'REG_DWORD_BIG_ENDIAN': 5,
            'REG_LINK': 6,
            'REG_MULTI_SZ': 7,
            'REG_RESOURCE_LIST': 8,
            'REG_FULL_RESOURCE_DESCRIPTOR': 9,
            'REG_RESOURCE_REQUIREMENTS_LIST': 10,
            'REG_QWORD': 11,
        }
        return fallback_map.get(reg_type, 1)  # Default to REG_SZ

    def _convert_from_samba_type(self, samba_type):
        """
        Convert Samba constant to registry type string

        Args:
            samba_type: Samba constant for registry type

        Returns:
            Registry type string
        """
        if hasattr(self, 'reg_type_reverse'):
            return self.reg_type_reverse.get(samba_type, 'REG_SZ')
        # Fallback mapping
        fallback_map = {
            0: 'REG_NONE',
            1: 'REG_SZ',
            2: 'REG_EXPAND_SZ',
            3: 'REG_BINARY',
            4: 'REG_DWORD',
            5: 'REG_DWORD_BIG_ENDIAN',
            6: 'REG_LINK',
            7: 'REG_MULTI_SZ',
            8: 'REG_RESOURCE_LIST',
            9: 'REG_FULL_RESOURCE_DESCRIPTOR',
            10: 'REG_RESOURCE_REQUIREMENTS_LIST',
            11: 'REG_QWORD',
        }
        return fallback_map.get(samba_type, 'REG_SZ')

    def _value_to_samba_data(self, value_data, reg_type):
        """
        Convert Python value to appropriate Samba entry data format

        Args:
            value_data: Python value (str, int, list, bytes)
            reg_type: Registry type constant (from samba.dcerpc.misc)

        Returns:
            Data formatted for preg.entry.data field
        """
        if not hasattr(self, 'reg_constants'):
            raise RuntimeError("Samba is not available: cannot convert registry data")
        misc = self.reg_constants
        if reg_type == misc.REG_SZ or reg_type == misc.REG_EXPAND_SZ:
            return str(value_data) if value_data is not None else ''
        elif reg_type == misc.REG_DWORD or reg_type == misc.REG_DWORD_BIG_ENDIAN or reg_type == misc.REG_QWORD:
            return int(value_data)
        elif reg_type == misc.REG_MULTI_SZ:
            if isinstance(value_data, list):
                # Join with null characters, double null terminate (UTF-16LE)
                if not value_data:
                    # Empty list encoded as double null terminator (two null characters)
                    return b'\x00\x00\x00\x00'
                # Ensure each element is string
                strings = [str(item) for item in value_data]
                data = u'\x00'.join(strings) + u'\x00\x00'
                return data.encode('utf-16le')
            else:
                # Assume it's a single string with embedded nulls? Not supported.
                raise ValueError("REG_MULTI_SZ value must be a list of strings")
        elif reg_type == misc.REG_BINARY:
            if isinstance(value_data, bytes):
                return value_data
            elif isinstance(value_data, str):
                # Assume hex string? For simplicity, encode as bytes
                return value_data.encode('utf-8')
            else:
                raise ValueError("REG_BINARY value must be bytes or string")
        elif reg_type == misc.REG_NONE:
            return None
        else:
            # Unknown type, treat as binary
            logger.warning(f"Unknown registry type {reg_type}, treating as binary")
            if isinstance(value_data, bytes):
                return value_data
            else:
                return str(value_data).encode('utf-8')

    def _samba_data_to_value(self, entry_data, reg_type):
        """
        Convert Samba entry data to Python value

        Args:
            entry_data: Data from preg.entry.data field
            reg_type: Registry type constant

        Returns:
            Python value (str, int, list, bytes)
        """
        if not hasattr(self, 'reg_constants'):
            raise RuntimeError("Samba is not available: cannot convert registry data")
        misc = self.reg_constants
        if reg_type == misc.REG_SZ or reg_type == misc.REG_EXPAND_SZ:
            return entry_data if entry_data is not None else ''
        elif reg_type == misc.REG_DWORD or reg_type == misc.REG_DWORD_BIG_ENDIAN or reg_type == misc.REG_QWORD:
            return int(entry_data) if entry_data is not None else 0
        elif reg_type == misc.REG_MULTI_SZ:
            if entry_data is None:
                return []
            # Decode utf-16le, preserve empty strings
            decoded = entry_data.decode('utf-16le')
            if not decoded:
                return []
            total_nulls = decoded.count(u'\x00')
            if total_nulls == 0:
                # Malformed REG_MULTI_SZ (no null terminators), treat as single string
                return [decoded]
            # Number of strings = total_nulls - 1 (extra terminator)
            num_strings = total_nulls - 1
            parts = decoded.split(u'\x00')
            # Remove last empty part caused by final null terminator
            if parts and parts[-1] == u'':
                parts.pop()
            # Now parts length should be total_nulls (delimiters)
            if num_strings <= len(parts):
                return parts[:num_strings]
            else:
                return parts
        elif reg_type == misc.REG_BINARY:
            return entry_data if entry_data is not None else b''
        elif reg_type == misc.REG_NONE:
            return None
        else:
            # Unknown type, return as is
            logger.warning(f"Unknown registry type {reg_type}, returning raw data")
            return entry_data

    def _get_gpt_ini_path(self, gpo_path):
        """
        Get path to GPT.INI file for a GPO.

        Args:
            gpo_path: Relative path to GPO within sysvol

        Returns:
            Path object to GPT.INI
        """
        gpo_full_path = self.sysvol_path / gpo_path
        utils.validate_path_in_sysvol(str(gpo_full_path), str(self.sysvol_path))
        return gpo_full_path / 'GPT.INI'

    def _parse_gpt_ini(self, gpt_ini_path):
        """
        Parse GPT.INI file.

        Args:
            gpt_ini_path: Path to GPT.INI

        Returns:
            dict with parsed key-value pairs from [General] section
        """
        result = {}
        in_general = False
        try:
            with open(gpt_ini_path, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if line == '[General]':
                        in_general = True
                        continue
                    if line.startswith('[') and line.endswith(']'):
                        in_general = False
                        continue
                    if in_general and '=' in line:
                        key, _, val = line.partition('=')
                        result[key.strip()] = val.strip()
        except FileNotFoundError:
            logger.debug(f"GPT.INI not found: {gpt_ini_path}")
        return result

    def _write_gpt_ini(self, gpt_ini_path, ini_data):
        """
        Write GPT.INI file from dict.

        Args:
            gpt_ini_path: Path to GPT.INI
            ini_data: dict with key-value pairs for [General] section
        """
        lines = ['[General]\n']
        for key, value in ini_data.items():
            lines.append('{}={}\n'.format(key, value))
        gpt_ini_path.write_text(''.join(lines), encoding='utf-8')

    def increment_gpo_version(self, gpo_path, scope='Machine'):
        """
        Increment GPO version in GPT.INI.

        The Version field encodes both User and Machine versions:
        Version = (UserVersion << 16) | MachineVersion

        Args:
            gpo_path: Relative path to GPO within sysvol
            scope: 'Machine' or 'User' — which version to increment

        Returns:
            True if successful, False otherwise
        """
        try:
            gpt_ini_path = self._get_gpt_ini_path(gpo_path)
            ini_data = self._parse_gpt_ini(gpt_ini_path)

            version_str = ini_data.get('Version', '0')
            try:
                version = int(version_str)
            except ValueError:
                version = 0

            machine_version = version & 0xFFFF
            user_version = (version >> 16) & 0xFFFF

            if scope == 'User':
                user_version += 1
            else:
                machine_version += 1

            new_version = (user_version << 16) | machine_version
            ini_data['Version'] = str(new_version)

            if 'displayName' not in ini_data:
                ini_data['displayName'] = 'New Group Policy Object'
            if 'flags' not in ini_data:
                ini_data['flags'] = '0'

            self._write_gpt_ini(gpt_ini_path, ini_data)
            logger.info("GPT.INI version updated to {} (User={}, Machine={})".format(
                new_version, user_version, machine_version))
            return True

        except (OSError, IOError) as e:
            logger.error("Failed to update GPT.INI version: {}".format(e))
            return False
        except Exception as e:
            logger.error("Unexpected error updating GPT.INI: {}".format(e))
            return False
