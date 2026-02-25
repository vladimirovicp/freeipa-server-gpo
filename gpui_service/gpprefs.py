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
GPPrefsWorker - Worker for Group Policy Preferences (GPP) XML file generation

Supports all GPP types specified in MS-GPPREF:
- Registry, Files, Folders, Shortcuts, Environment, IniFiles
- Users, Groups, Drives, Printers, Services, ScheduledTasks
"""

import logging
import json
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from datetime import datetime
import traceback
import re

logger = logging.getLogger('gpuiservice')

class GPPrefsWorker:
    """
    Worker for Group Policy Preferences XML file generation and management

    This class provides functionality to create, read, update, and delete
    Group Policy Preferences XML files according to MS-GPPREF specification.
    """

    # CLSID mapping for each preference type (Inner Element CLSID from MS-GPPREF)
    CLSID_MAP = {
        'Registry': '{9CD4B2F4-923D-47f5-A062-E897DD1DAD50}',
        'Files': '{50BE44C8-567A-4ed1-B1D0-9234FE1F38AF}',
        'Folders': '{07DA02F5-F9CD-4397-A550-4AE21B6B4BD3}',
        'Shortcuts': '{4F2F7C55-2790-433e-8127-0739D1CFA327}',
        'Environment': '{78570023-8373-4a19-BA80-2F150738EA19}',
        'IniFiles': '{EEFACE84-D3D8-4680-8D4B-BF103E759448}',
        'Users': '{DF5F1855-51E5-4d24-8B1A-D9BDE98BA1D1}',
        'Groups': '{6D4A79E4-529C-4481-ABD0-F5BD7EA93BA7}',
        'Drives': '{935D1B74-9CB8-4e3c-9914-7DD559B7A417}',
        'Printers': '{9A5E9697-9095-436d-A0EE-4D128FDFBCE5}',  # SharedPrinter (others available)
        'Services': '{AB6F0B67-341F-4e51-92F9-005FBFBA1A43}',
        'ScheduledTasks': '{2DEECB1C-261F-4e13-9B21-16FB83BC03BD}',  # Task (others available)
    }

    # File name mapping (XML file names for each type)
    FILE_NAME_MAP = {
        'Registry': 'registry.xml',
        'Files': 'files.xml',
        'Folders': 'folders.xml',
        'Shortcuts': 'shortcuts.xml',
        'Environment': 'environment.xml',
        'IniFiles': 'ini.xml',
        'Users': 'users.xml',
        'Groups': 'groups.xml',
        'Drives': 'drives.xml',
        'Printers': 'printers.xml',
        'Services': 'services.xml',
        'ScheduledTasks': 'scheduledtasks.xml',
    }

    # Valid actions for each type (U=Update, C=Create, R=Replace, D=Delete)
    VALID_ACTIONS = ['U', 'C', 'R', 'D']

    # Required and optional properties for each preference type
    PROPERTY_SCHEMAS = {
        'Registry': {
            'required': ['action', 'hive', 'key', 'name', 'type', 'value'],
            'optional': [],
        },
        'Files': {
            'required': ['action', 'sourcePath', 'targetPath'],
            'optional': ['readOnly', 'archive', 'hidden', 'suppressErrors'],
        },
        'Folders': {
            'required': ['action', 'targetPath'],
            'optional': ['readOnly', 'archive', 'hidden', 'suppressErrors'],
        },
        'Shortcuts': {
            'required': ['action', 'targetPath'],
            'optional': ['shortcutPath', 'arguments', 'iconPath', 'iconIndex', 'windowStyle'],
        },
        'Environment': {
            'required': ['action', 'user', 'name', 'value'],
            'optional': ['append', 'remove'],
        },
        'IniFiles': {
            'required': ['action', 'iniPath', 'section', 'property', 'value'],
            'optional': [],
        },
        'Users': {
            'required': ['action', 'userName'],
            'optional': ['fullName', 'description', 'password', 'cpassword', 'acctDisabled',
                        'neverExpires', 'passwordNeverExpires', 'userMustChangePwd'],
        },
        'Groups': {
            'required': ['action', 'groupName'],
            'optional': ['description', 'members', 'deleteAllUsers', 'deleteAllGroups'],
        },
        'Drives': {
            'required': ['action', 'driveLetter'],
            'optional': ['path', 'label', 'persistent', 'useLetter'],
        },
        'Printers': {
            'required': ['action', 'printerName'],
            'optional': ['port', 'path', 'location', 'comment', 'default', 'skipLocal'],
        },
        'Services': {
            'required': ['action', 'serviceName'],
            'optional': ['startupType', 'serviceAction', 'arguments', 'waitTimeout'],
        },
        'ScheduledTasks': {
            'required': ['action', 'taskName'],
            'optional': ['runAs', 'command', 'arguments', 'startTime', 'days', 'months'],
        },
    }

    def __init__(self, sysvol_path='/var/lib/freeipa/sysvol'):
        """
        Initialize GPPrefs worker

        Args:
            sysvol_path: Path to FreeIPA sysvol directory where GPT structures are stored
        """
        self.sysvol_path = Path(sysvol_path)
        logger.debug(f"GPPrefsWorker initialized with sysvol path: {sysvol_path}")

    def _get_preferences_path(self, gpo_guid, scope):
        """
        Get path to Preferences directory for a GPO

        Args:
            gpo_guid: GUID or name of the GPO directory (e.g., 'gpt1test' or '{GUID}')
            scope: 'Machine' or 'User'

        Returns:
            Path object to the Preferences directory
        """
        # Structure: sysvol_path/{gpo_guid}/{scope}/Preferences
        return self.sysvol_path / gpo_guid / scope / 'Preferences'

    def _get_xml_file_path(self, gpo_guid, scope, pref_type):
        """
        Get full path to XML file for a preference type

        Args:
            gpo_guid: GUID of the GPO
            scope: 'Machine' or 'User'
            pref_type: Preference type (Registry, Files, etc.)

        Returns:
            Path object to the XML file
        """
        pref_dir = self._get_preferences_path(gpo_guid, scope)
        xml_file_name = self.FILE_NAME_MAP.get(pref_type)
        if not xml_file_name:
            xml_file_name = f"{pref_type.lower()}.xml"
        return pref_dir / pref_type / xml_file_name

    def _validate_json(self, data):
        """
        Validate input JSON structure

        Args:
            data: dict parsed from JSON

        Raises:
            ValueError: if validation fails
        """
        required = ['gpo_guid', 'scope', 'preferences']
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        if data['scope'] not in ['Machine', 'User']:
            raise ValueError("scope must be 'Machine' or 'User'")

        if not isinstance(data['preferences'], list):
            raise ValueError("preferences must be a list")

        for pref in data['preferences']:
            if 'type' not in pref:
                raise ValueError("Each preference must have 'type' field")
            if pref['type'] not in self.CLSID_MAP:
                raise ValueError(f"Unknown preference type: {pref['type']}")
            if 'properties' not in pref:
                raise ValueError(f"Preference {pref.get('uid', 'unknown')} missing 'properties'")
            # Validate action if present
            if 'action' in pref['properties']:
                if pref['properties']['action'] not in self.VALID_ACTIONS:
                    raise ValueError(f"Invalid action: {pref['properties']['action']}")

            # Validate properties for the specific type
            self._validate_properties(pref['type'], pref['properties'])

    def _validate_properties(self, pref_type, properties):
        """
        Validate properties for a specific preference type

        Args:
            pref_type: Type of preference
            properties: dict of properties

        Raises:
            ValueError: if validation fails
        """
        if pref_type not in self.PROPERTY_SCHEMAS:
            raise ValueError(f"No property schema defined for type: {pref_type}")

        schema = self.PROPERTY_SCHEMAS[pref_type]

        # Check required properties
        for prop in schema['required']:
            if prop not in properties:
                raise ValueError(f"Missing required property '{prop}' for {pref_type}")

        # Check for unknown properties
        allowed = set(schema['required'] + schema['optional'])
        for prop in properties.keys():
            if prop not in allowed:
                raise ValueError(f"Unknown property '{prop}' for {pref_type}. Allowed: {sorted(allowed)}")

        # Type-specific validation
        if pref_type == 'Registry':
            self._validate_registry_properties(properties)
        elif pref_type == 'Files':
            self._validate_files_properties(properties)
        elif pref_type == 'Environment':
            self._validate_environment_properties(properties)
        elif pref_type == 'Users':
            self._validate_users_properties(properties)
        # Add other type-specific validations as needed

    def _validate_registry_properties(self, properties):
        """Validate Registry properties"""
        hive = properties.get('hive')
        if hive and hive not in ['HKEY_LOCAL_MACHINE', 'HKEY_CURRENT_USER',
                                 'HKEY_CLASSES_ROOT', 'HKEY_USERS', 'HKEY_CURRENT_CONFIG']:
            raise ValueError(f"Invalid hive: {hive}")

        reg_type = properties.get('type')
        if reg_type and reg_type not in ['REG_SZ', 'REG_EXPAND_SZ', 'REG_BINARY',
                                         'REG_DWORD', 'REG_DWORD_BIG_ENDIAN',
                                         'REG_LINK', 'REG_MULTI_SZ', 'REG_QWORD',
                                         'REG_NONE']:
            raise ValueError(f"Invalid registry type: {reg_type}")

    def _validate_files_properties(self, properties):
        """Validate Files properties"""
        # Validate paths
        source = properties.get('sourcePath')
        target = properties.get('targetPath')
        if source and not source.strip():
            raise ValueError("sourcePath cannot be empty")
        if target and not target.strip():
            raise ValueError("targetPath cannot be empty")

    def _validate_environment_properties(self, properties):
        """Validate Environment properties"""
        user = properties.get('user')
        if user is not None:
            if isinstance(user, str):
                if user.lower() not in ['true', 'false', '0', '1']:
                    raise ValueError("user must be boolean or 'true'/'false'")
            elif not isinstance(user, bool):
                raise ValueError("user must be boolean")

    def _validate_users_properties(self, properties):
        """Validate Users properties"""
        # Password handling warning
        if 'password' in properties:
            logger.warning("Storing password in plaintext is insecure. Use cpassword with encryption.")
        # Validate boolean fields
        bool_fields = ['acctDisabled', 'neverExpires', 'passwordNeverExpires', 'userMustChangePwd']
        for field in bool_fields:
            if field in properties:
                val = properties[field]
                if isinstance(val, str) and val.lower() not in ['true', 'false', '0', '1']:
                    raise ValueError(f"{field} must be boolean")

    def _ensure_uid(self, pref):
        """
        Ensure preference has a valid UID

        Args:
            pref: preference dict

        Returns:
            preference dict with ensured UID
        """
        if 'uid' not in pref or not pref['uid']:
            pref['uid'] = str(uuid.uuid4()).upper()
        else:
            # Validate GUID format
            uid = pref['uid']
            guid_pattern = r'^\{?[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}\}?$'
            if not re.match(guid_pattern, uid, re.IGNORECASE):
                raise ValueError(f"Invalid UID format: {uid}")
        return pref

    def _ensure_changed(self, pref):
        """
        Ensure preference has a changed timestamp

        Args:
            pref: preference dict

        Returns:
            preference dict with ensured changed timestamp
        """
        if 'changed' not in pref or not pref['changed']:
            # ISO 8601 format without microseconds, space separated
            pref['changed'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return pref

    def _encrypt_password(self, password):
        """
        Encrypt password for cpassword field using MS-GPPREF algorithm

        Args:
            password: plaintext password

        Returns:
            Base64-encoded encrypted password
        """
        # Microsoft's 32-byte AES key for GPP
        key = bytes([
            0x4e, 0x99, 0x06, 0xe8, 0xfc, 0xb6, 0x6c, 0xc9,
            0xfa, 0xf4, 0x93, 0x10, 0x62, 0x0f, 0xfe, 0xe8,
            0xf4, 0x96, 0xe8, 0x06, 0xcc, 0x05, 0x79, 0x90,
            0x20, 0x9b, 0x09, 0xa4, 0x33, 0xb6, 0x6c, 0x1b
        ])

        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            import base64

            # AES-256-CBC with IV of zeros
            iv = b'\x00' * 16
            cipher = AES.new(key, AES.MODE_CBC, iv)
            # Pad password to 16-byte boundary
            padded = pad(password.encode('utf-16le'), AES.block_size)
            encrypted = cipher.encrypt(padded)
            return base64.b64encode(encrypted).decode('ascii')

        except ImportError:
            logger.error("PyCryptodome not available. Password encryption disabled.")
            # Return empty string or raise error
            return ""
        except Exception as e:
            logger.error(f"Failed to encrypt password: {e}")
            return ""

    def _bool_to_int(self, value):
        """
        Convert boolean to integer (0 or 1) for XML attributes

        Args:
            value: boolean or string representation

        Returns:
            '0' for False, '1' for True
        """
        if isinstance(value, bool):
            return '1' if value else '0'
        if isinstance(value, str):
            if value.lower() in ('true', '1', 'yes', 'on'):
                return '1'
            elif value.lower() in ('false', '0', 'no', 'off'):
                return '0'
        # Try integer conversion
        try:
            return '1' if int(value) else '0'
        except (ValueError, TypeError):
            return '0'

    def _create_properties_element(self, pref_type, properties):
        """
        Create <Properties> element for a preference

        Args:
            pref_type: Type of preference
            properties: dict of properties

        Returns:
            ET.Element for Properties
        """
        props_elem = ET.Element('Properties')

        # Handle password encryption for Users/Groups
        processed_props = properties.copy()
        if pref_type in ['Users', 'Groups'] and 'password' in processed_props:
            password = processed_props.pop('password')
            if password:
                cpassword = self._encrypt_password(password)
                if cpassword:
                    processed_props['cpassword'] = cpassword
                    logger.warning("Password encrypted as cpassword (insecure). Consider using alternative mechanisms.")
                else:
                    logger.error("Failed to encrypt password, cpassword will be empty")
            # If password is empty string, don't add cpassword

        for key, value in processed_props.items():
            if value is None:
                continue
            if isinstance(value, bool):
                props_elem.set(key, self._bool_to_int(value))
            else:
                props_elem.set(key, str(value))
        return props_elem

    def _create_filter_element(self, filters):
        """
        Create <Filters> element for item-level targeting

        Args:
            filters: dict with 'operator' and 'conditions'

        Returns:
            ET.Element for Filters or None
        """
        if not filters:
            return None

        filters_elem = ET.Element('Filters')
        operator = filters.get('operator', 'AND')
        filters_elem.set('bool', operator)

        for condition in filters.get('conditions', []):
            cond_type = condition.get('type')
            if not cond_type:
                continue

            cond_elem = ET.Element(f'Filter{cond_type}')
            for key, value in condition.items():
                if key == 'type':
                    continue
                if isinstance(value, bool):
                    cond_elem.set(key, self._bool_to_int(value))
                else:
                    cond_elem.set(key, str(value))
            filters_elem.append(cond_elem)

        return filters_elem

    def _create_preference_element(self, pref):
        """
        Create XML element for a single preference

        Args:
            pref: preference dict

        Returns:
            ET.Element for the preference
        """
        pref_type = pref['type']
        clsid = self.CLSID_MAP[pref_type]

        # Create root element for this preference
        pref_elem = ET.Element(pref_type)
        pref_elem.set('clsid', clsid)
        pref_elem.set('name', pref.get('name', ''))
        pref_elem.set('uid', pref['uid'])
        pref_elem.set('changed', pref['changed'])

        bypass_errors = pref.get('bypassErrors', False)
        if bypass_errors:
            pref_elem.set('bypassErrors', '1')

        # Add Properties
        props_elem = self._create_properties_element(pref_type, pref['properties'])
        pref_elem.append(props_elem)

        # Add Filters if present
        if 'filters' in pref:
            filters_elem = self._create_filter_element(pref['filters'])
            if filters_elem is not None:
                pref_elem.append(filters_elem)

        return pref_elem

    def save_preferences(self, json_data):
        """
        Save preferences to XML files in SYSVOL

        Args:
            json_data: JSON string or dict containing preferences

        Returns:
            dict with results: {'success': bool, 'message': str, 'files': list}
        """
        try:
            # Parse JSON if string
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data

            # Validate input
            self._validate_json(data)

            gpo_guid = data['gpo_guid']
            scope = data['scope']

            # Group preferences by type for separate XML files
            prefs_by_type = {}
            for pref in data['preferences']:
                pref = self._ensure_uid(pref)
                pref = self._ensure_changed(pref)
                pref_type = pref['type']
                if pref_type not in prefs_by_type:
                    prefs_by_type[pref_type] = []
                prefs_by_type[pref_type].append(pref)

            saved_files = []
            errors = []

            # Process each preference type separately
            for pref_type, prefs in prefs_by_type.items():
                try:
                    xml_path = self._get_xml_file_path(gpo_guid, scope, pref_type)
                    xml_path.parent.mkdir(parents=True, exist_ok=True)

                    # Read existing XML if present
                    collection = self._read_or_create_collection(xml_path, pref_type)

                    # Add or update preferences in collection
                    for pref in prefs:
                        self._update_collection(collection, pref)

                    # Write XML
                    xml_content = self._pretty_xml(collection)
                    xml_path.write_text(xml_content, encoding='utf-8')
                    saved_files.append(str(xml_path))

                    logger.info(f"Saved {len(prefs)} {pref_type} preferences to {xml_path}")

                except Exception as e:
                    error_msg = f"Failed to save {pref_type} preferences: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    errors.append(error_msg)

            if errors:
                return {
                    'success': False,
                    'message': f"Partial success with errors: {'; '.join(errors)}",
                    'files': saved_files,
                    'errors': errors
                }

            return {
                'success': True,
                'message': f"Successfully saved preferences to {len(saved_files)} file(s)",
                'files': saved_files
            }

        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'message': str(e),
                'files': []
            }

    def _read_or_create_collection(self, xml_path, pref_type):
        """
        Read existing XML file or create new Collection element

        Args:
            xml_path: Path or str to XML file
            pref_type: Preference type

        Returns:
            ET.Element for Collection
        """
        from pathlib import Path
        xml_path = Path(xml_path)
        if xml_path.exists():
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                if root.tag == 'Collection':
                    return root
                else:
                    logger.warning(f"Root element is not Collection in {xml_path}, creating new")
            except ET.ParseError as e:
                logger.warning(f"Failed to parse XML file {xml_path}: {e}, creating new")

        # Create new Collection
        clsid = self.CLSID_MAP[pref_type]
        collection = ET.Element('Collection')
        collection.set('clsid', clsid)
        return collection

    def _update_collection(self, collection, pref):
        """
        Update collection with a preference (add or replace by uid)

        Args:
            collection: Collection ET.Element
            pref: preference dict
        """
        pref_uid = pref['uid']
        # Remove existing preference with same UID
        for elem in collection.findall('*'):
            if elem.get('uid') == pref_uid:
                collection.remove(elem)
                break

        # Add new preference element
        pref_elem = self._create_preference_element(pref)
        collection.append(pref_elem)

    def _pretty_xml(self, element):
        """
        Convert XML element to pretty-printed string

        Args:
            element: ET.Element

        Returns:
            Pretty-printed XML string
        """
        rough_string = ET.tostring(element, 'utf-8')
        parsed = minidom.parseString(rough_string)
        # toprettyxml already includes XML declaration
        return parsed.toprettyxml(indent='  ')

    def read_preferences(self, gpo_guid, scope, pref_type=None):
        """
        Read preferences from XML files

        Args:
            gpo_guid: GUID of the GPO
            scope: 'Machine' or 'User'
            pref_type: Specific preference type to read, or None for all

        Returns:
            dict with preferences grouped by type
        """
        result = {}

        if pref_type:
            types_to_read = [pref_type]
        else:
            types_to_read = self.CLSID_MAP.keys()

        for ptype in types_to_read:
            try:
                xml_path = self._get_xml_file_path(gpo_guid, scope, ptype)
                if not xml_path.exists():
                    continue

                tree = ET.parse(xml_path)
                collection = tree.getroot()
                if collection.tag != 'Collection':
                    logger.warning(f"Root element is not Collection in {xml_path}")
                    continue

                preferences = []
                for pref_elem in collection.findall('*'):
                    pref = self._parse_preference_element(pref_elem)
                    preferences.append(pref)

                result[ptype] = preferences

            except Exception as e:
                logger.error(f"Failed to read {ptype} preferences: {e}")

        return result

    def _parse_preference_element(self, pref_elem):
        """
        Parse XML preference element back to dict

        Args:
            pref_elem: ET.Element

        Returns:
            dict representation of preference
        """
        pref = {
            'type': pref_elem.tag,
            'uid': pref_elem.get('uid', ''),
            'name': pref_elem.get('name', ''),
            'changed': pref_elem.get('changed', ''),
            'bypassErrors': pref_elem.get('bypassErrors', '0') == '1'
        }

        # Parse Properties
        props_elem = pref_elem.find('Properties')
        if props_elem is not None:
            properties = {}
            for key, value in props_elem.items():
                # Convert numeric strings to int if possible
                if value.isdigit():
                    properties[key] = int(value)
                elif value.lower() in ('true', 'false'):
                    properties[key] = value.lower() == 'true'
                else:
                    properties[key] = value
            pref['properties'] = properties

        # Parse Filters
        filters_elem = pref_elem.find('Filters')
        if filters_elem is not None:
            filters = {
                'operator': filters_elem.get('bool', 'AND'),
                'conditions': []
            }
            for filter_elem in filters_elem:
                condition = {'type': filter_elem.tag.replace('Filter', '')}
                for key, value in filter_elem.items():
                    if value.isdigit():
                        condition[key] = int(value)
                    elif value.lower() in ('true', 'false'):
                        condition[key] = value.lower() == 'true'
                    else:
                        condition[key] = value
                filters['conditions'].append(condition)
            pref['filters'] = filters

        return pref

    def delete_preference(self, gpo_guid, scope, pref_type, uid):
        """
        Delete a specific preference by UID

        Args:
            gpo_guid: GUID of the GPO
            scope: 'Machine' or 'User'
            pref_type: Type of preference
            uid: UID of the preference to delete

        Returns:
            True if deleted, False otherwise
        """
        try:
            xml_path = self._get_xml_file_path(gpo_guid, scope, pref_type)
            if not xml_path.exists():
                logger.debug(f"XML file not found: {xml_path}")
                return False

            tree = ET.parse(xml_path)
            collection = tree.getroot()
            if collection.tag != 'Collection':
                logger.warning(f"Root element is not Collection in {xml_path}")
                return False

            # Find and remove element with matching UID
            removed = False
            for elem in collection.findall('*'):
                if elem.get('uid') == uid:
                    collection.remove(elem)
                    removed = True
                    break

            if removed:
                # If collection becomes empty, delete the file
                if len(collection) == 0:
                    xml_path.unlink()
                    logger.info(f"Deleted empty XML file: {xml_path}")
                else:
                    xml_content = self._pretty_xml(collection)
                    xml_path.write_text(xml_content, encoding='utf-8')
                    logger.info(f"Deleted preference {uid} from {xml_path}")
                return True
            else:
                logger.debug(f"Preference with UID {uid} not found in {xml_path}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete preference: {e}")
            logger.error(traceback.format_exc())
            return False