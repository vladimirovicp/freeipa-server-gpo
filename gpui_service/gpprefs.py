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
- Drives, Printers, Services, ScheduledTasks
"""

import logging
import json
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
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
    OUTER_CLSID_MAP = {
        'Registry': '{35378EAC-683F-11D2-A89A-00C04FBBCFA2}',
        'Files': '{7B849a34-0AB9-4CFF-92B2-5C5D5B26F0CE}',
        'Folders': '{B087BE9D-ED37-454F-AF9C-04291E351182}',
        'Shortcuts': '{C418DD9D-0D14-4EFB-8FBF-CFE535C8FAC7}',
        'Environment': '{78570023-8373-4A19-BA80-2F150738EA19}',
        'IniFiles': '{EEFACE84-D3D8-4680-8D4B-BF103E759448}',
        'Drives': '{5794DAFD-BE60-433F-88A2-1A31939AC01F}',
        'Printers': '{BC75B1ED-5833-4858-9BB8-CBF0B166DF9D}',
        'Services': '{91FBB303-0CD5-4055-BF42-E512A681B325}',
        'ScheduledTasks': '{AADCED64-746C-4633-A97C-D61349046527}',
        'NetworkShares': '{B087BE9D-ED37-454F-AF9C-04291E351182}',
    }

    # File name mapping (XML file names for each type)
    INNER_CLSID_MAP = {
        'Registry': '{9CD4B2F4-923D-47F5-A062-E897DD1DAD50}',
        'Files': '{50BE44C8-567A-4ED1-B1D0-9234FE1F38AF}',
        'Folders': '{07DA02F5-F9CD-4397-A550-4AE21B6B4BD3}',
        'Shortcuts': '{4F2F7C55-2790-433E-8127-0739D1CFA327}',
        'Environment': '{78570023-8373-4A19-BA80-2F150738EA19}',
        'IniFiles': '{EEFACE84-D3D8-4680-8D4B-BF103E759448}',
        'Drives': '{935D1B74-9CB8-4E3C-9914-7DD559B7A417}',
        'Printers': '{9A5E9697-9095-436D-A0EE-4D128FDFBCE5}',
        'Services': '{AB6F0B67-341F-4E51-92F9-005FBFBA1A43}',
        'ScheduledTasks': '{2DEECB1C-261F-4E13-9B21-16FB83BC03BD}',
        'NetworkShares': '{2888C5E7-94FC-4739-90AA-2C1536D68BC0}',
    }

    # XML file names for each preference type
    FILE_NAME_MAP = {
        'Registry': 'RegistrySettings.xml',
        'Files': 'Files.xml',
        'Folders': 'Folders.xml',
        'Shortcuts': 'Shortcuts.xml',
        'Environment': 'EnvironmentVariables.xml',
        'IniFiles': 'IniFiles.xml',
        'Drives': 'Drives.xml',
        'Printers': 'Printers.xml',
        'Services': 'Services.xml',
        'ScheduledTasks': 'ScheduledTasks.xml',
        'NetworkShares': 'NetworkShareSettings.xml',
    }

    # Valid actions for each type (U=Update, C=Create, R=Replace, D=Delete)
    VALID_ACTIONS = ['U', 'C', 'R', 'D']

    # Required and optional properties for each preference type (inside <Properties> element)
    # Based on MS-GPPREF XML schemas. Common attributes (clsid, name, uid, changed, desc, bypassErrors, userContext, removePolicy, image, status) are on the preference element.
    PROPERTY_SCHEMAS = {
        'Registry': {
            'required': ['hive', 'key'],
            'optional': ['action', 'default', 'name', 'type', 'value', 'displayDecimal', 'defaultValue', 'bitfield', 'disabled', 'SubProp'],
        },
        'Files': {
            'required': ['fromPath', 'targetPath'],
            'optional': ['action', 'readOnly', 'archive', 'hidden', 'suppress', 'disabled'],
        },
        'Folders': {
            'required': ['path', 'readOnly', 'archive', 'hidden'],
            'optional': ['action', 'deleteSubFolders', 'deleteFiles', 'deleteFolder', 'deleteReadOnly', 'deleteIgnoreErrors', 'disabled'],
        },
        'Shortcuts': {
            'required': ['targetType', 'targetPath', 'shortcutPath'],
            'optional': ['pidl', 'action', 'comment', 'shortcutKey', 'startIn', 'arguments', 'iconIndex', 'iconPath', 'window', 'disabled'],
        },
        'Environment': {
            'required': ['name', 'value'],
            'optional': ['action', 'user', 'partial', 'disabled'],
        },
        'IniFiles': {
            'required': ['path'],
            'optional': ['section', 'value', 'property', 'action', 'disabled'],
        },
        'Drives': {
            'required': ['path', 'persistent', 'useLetter', 'letter'],
            'optional': ['action', 'thisDrive', 'allDrives', 'userName', 'cpassword', 'label', 'disabled'],
        },
        'Printers': {
            'required': ['path', 'port'],
            'optional': ['action', 'comment', 'location', 'default', 'skipLocal', 'deleteAll', 'persistent', 'deleteMaps', 'username', 'cpassword', 'disabled'],
        },
        'Services': {
            'required': ['serviceName'],
            'optional': ['action', 'startupType', 'serviceAction', 'arguments', 'waitTimeout', 'account', 'password', 'disabled'],
        },
        'ScheduledTasks': {
            'required': ['name', 'appName', 'enabled'],
            'optional': ['action', 'args', 'startIn', 'comment', 'maxRunTime', 'runAs', 'cpassword', 'deleteWhenDone', 'deadlineMinutes', 'startOnlyIfIdle', 'stopOnIdleEnd', 'noStartIfOnBatteries', 'stopIfGoingOnBatteries', 'systemRequired', 'disabled', 'Triggers'],
        },
        'NetworkShares': {
            'required': ['name', 'path', 'comment'],
            'optional': ['action', 'allRegular', 'allHidden', 'allAdminDrive', 'limitUsers', 'abe', 'userLimit', 'disabled'],
        },
    }

    def __init__(self, sysvol_path='/var/lib/freeipa/sysvol'):
        """
        Initialize GPPrefs worker

        Args:
            sysvol_path: Path to FreeIPA sysvol directory where GPT structures are stored
        """
        self.sysvol_path = sysvol_path
        logger.debug("GPPrefsWorker initialized with sysvol path: {}".format(sysvol_path))

    def _get_preferences_path(self, gpo_guid, scope):
        """
        Get path to Preferences directory for a GPO

        Args:
            gpo_guid: GUID or name of the GPO directory (e.g., 'gpt1test' or '{GUID}')
            scope: 'Machine' or 'User'

        Returns:
            string path to the Preferences directory
        """
        # Structure: sysvol_path/{gpo_guid}/{scope}/Preferences
        return os.path.join(self.sysvol_path, gpo_guid, scope, 'Preferences')

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
            xml_file_name = "{}.xml".format(pref_type.lower())
        return Path(os.path.join(pref_dir, pref_type, xml_file_name))

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
                raise ValueError("Missing required field: {}".format(field))

        if data['scope'] not in ['Machine', 'User']:
            raise ValueError("scope must be 'Machine' or 'User'")

        if not isinstance(data['preferences'], list):
            raise ValueError("preferences must be a list")

        for pref in data['preferences']:
            if 'type' not in pref:
                raise ValueError("Each preference must have 'type' field")
            if pref['type'] not in self.OUTER_CLSID_MAP:
                raise ValueError("Unknown preference type: {}".format(pref['type']))
            if 'properties' not in pref:
                raise ValueError("Preference {} missing 'properties'".format(pref.get('uid', 'unknown')))
            # Validate action if present
            if 'action' in pref['properties']:
                if pref['properties']['action'] not in self.VALID_ACTIONS:
                    raise ValueError("Invalid action: {}".format(pref['properties']['action']))

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
            raise ValueError("No property schema defined for type: {}".format(pref_type))

        schema = self.PROPERTY_SCHEMAS[pref_type]

        # Check required properties
        for prop in schema['required']:
            if prop not in properties:
                raise ValueError("Missing required property '{}' for {}".format(prop, pref_type))

        # Check for unknown properties
        allowed = set(schema['required'] + schema['optional'])
        for prop in properties.keys():
            if prop not in allowed:
                raise ValueError("Unknown property '{}' for {}. Allowed: {}".format(prop, pref_type, sorted(allowed)))

        # Type-specific validation
        if pref_type == 'Registry':
            self._validate_registry_properties(properties)
        elif pref_type == 'Files':
            self._validate_files_properties(properties)
        elif pref_type == 'Folders':
            self._validate_folders_properties(properties)
        elif pref_type == 'Shortcuts':
            self._validate_shortcuts_properties(properties)
        elif pref_type == 'Environment':
            self._validate_environment_properties(properties)
        elif pref_type == 'IniFiles':
            self._validate_inifiles_properties(properties)
        elif pref_type == 'Drives':
            self._validate_drives_properties(properties)
        elif pref_type == 'Printers':
            self._validate_printers_properties(properties)
        elif pref_type == 'Services':
            self._validate_services_properties(properties)
        elif pref_type == 'ScheduledTasks':
            self._validate_scheduled_tasks_properties(properties)
        elif pref_type == 'NetworkShares':
            self._validate_network_shares_properties(properties)

    def _validate_registry_properties(self, properties):
        """Validate Registry properties"""
        # Validate hive
        hive = properties.get('hive')
        if hive and hive not in ['HKEY_LOCAL_MACHINE', 'HKEY_CURRENT_USER',
                                 'HKEY_CLASSES_ROOT', 'HKEY_USERS', 'HKEY_CURRENT_CONFIG']:
            raise ValueError("Invalid hive: {}".format(hive))

        # Validate key not empty
        key = properties.get('key')
        if key and not key.strip():
            raise ValueError("key cannot be empty")

        # Validate action enum
        action = properties.get('action')
        if action and action not in ['C', 'D', 'R', 'U']:
            raise ValueError("Invalid action: {}. Must be C, D, R, or U".format(action))

        # Validate boolean properties
        bool_props = ['default', 'displayDecimal', 'disabled']
        for prop in bool_props:
            val = properties.get(prop)
            if val is not None:
                if isinstance(val, str):
                    if val.lower() not in ['true', 'false', '0', '1']:
                        raise ValueError("{} must be boolean or 'true'/'false'".format(prop))
                elif not isinstance(val, bool):
                    raise ValueError("{} must be boolean".format(prop))

        # Validate numeric properties (xs:unsignedByte)
        # Note: 'value' is a registry value string and must NOT be validated as a numeric byte
        numeric_props = ['bitfield', 'defaultValue']
        for prop in numeric_props:
            val = properties.get(prop)
            if val is not None:
                try:
                    num = int(val)
                    if num < 0 or num > 255:
                        raise ValueError("{} must be between 0 and 255".format(prop))
                except (ValueError, TypeError):
                    raise ValueError("{} must be an integer between 0 and 255".format(prop))

        # Validate name not empty if present
        name = properties.get('name')
        if name and not name.strip():
            raise ValueError("name cannot be empty")

        # Validate type enum
        reg_type = properties.get('type')
        if reg_type and reg_type not in ['REG_SZ', 'REG_EXPAND_SZ', 'REG_BINARY',
                                         'REG_DWORD', 'REG_DWORD_BIG_ENDIAN',
                                         'REG_LINK', 'REG_MULTI_SZ', 'REG_QWORD',
                                         'REG_NONE']:
            raise ValueError("Invalid registry type: {}".format(reg_type))

        # Validate default vs name relationship
        # Use key presence check to correctly handle explicit False values
        has_default = properties.get('default') not in (None, False, 'false', '0')
        has_name = bool(properties.get('name'))
        if has_default and has_name:
            raise ValueError("Cannot specify both 'default' and 'name' for registry value")

    def _validate_files_properties(self, properties):
        """Validate Files properties"""
        # Validate paths
        from_path = properties.get('fromPath')
        target_path = properties.get('targetPath')
        if from_path and not from_path.strip():
            raise ValueError("fromPath cannot be empty")
        if target_path and not target_path.strip():
            raise ValueError("targetPath cannot be empty")
        # Validate boolean properties
        bool_props = ['readOnly', 'archive', 'hidden', 'suppress', 'disabled']
        for prop in bool_props:
            val = properties.get(prop)
            if val is not None:
                if isinstance(val, str):
                    if val.lower() not in ['true', 'false', '0', '1']:
                        raise ValueError("{} must be boolean or 'true'/'false'".format(prop))
                elif not isinstance(val, bool):
                    raise ValueError("{} must be boolean".format(prop))

    def _validate_environment_properties(self, properties):
        """Validate Environment properties"""
        # Validate name and value not empty
        name = properties.get('name')
        if name and not name.strip():
            raise ValueError("name cannot be empty")
        value = properties.get('value')
        if value and not value.strip():
            raise ValueError("value cannot be empty")

        # Validate action enum
        action = properties.get('action')
        if action and action not in ['C', 'D', 'R', 'U']:
            raise ValueError("Invalid action: {}. Must be C, D, R, or U".format(action))

        # Validate boolean properties
        bool_props = ['user', 'partial', 'disabled']
        for prop in bool_props:
            val = properties.get(prop)
            if val is not None:
                if isinstance(val, str):
                    if val.lower() not in ['true', 'false', '0', '1']:
                        raise ValueError("{} must be boolean or 'true'/'false'".format(prop))
                elif not isinstance(val, bool):
                    raise ValueError("{} must be boolean".format(prop))


    def _validate_folders_properties(self, properties):
        """Validate Folders properties"""
        # Validate path not empty
        path = properties.get('path')
        if path and not path.strip():
            raise ValueError("path cannot be empty")

        # Validate action enum
        action = properties.get('action')
        if action and action not in ['C', 'D', 'R', 'U']:
            raise ValueError("Invalid action: {}. Must be C, D, R, or U".format(action))

        # Validate required boolean properties (readOnly, archive, hidden)
        bool_props = ['readOnly', 'archive', 'hidden', 'disabled']
        for prop in bool_props:
            val = properties.get(prop)
            if val is not None:
                if isinstance(val, str):
                    if val.lower() not in ['true', 'false', '0', '1']:
                        raise ValueError("{} must be boolean or 'true'/'false'".format(prop))
                elif not isinstance(val, bool):
                    raise ValueError("{} must be boolean".format(prop))

        # Validate delete* properties (xs:unsignedByte)
        delete_props = ['deleteSubFolders', 'deleteFiles', 'deleteFolder', 'deleteReadOnly', 'deleteIgnoreErrors']
        for prop in delete_props:
            val = properties.get(prop)
            if val is not None:
                try:
                    num = int(val)
                    if num < 0 or num > 255:
                        raise ValueError("{} must be between 0 and 255".format(prop))
                except (ValueError, TypeError):
                    raise ValueError("{} must be an integer between 0 and 255".format(prop))

    def _validate_shortcuts_properties(self, properties):
        """Validate Shortcuts properties"""
        # Check required properties
        for prop in ['targetType', 'targetPath', 'shortcutPath']:
            val = properties.get(prop)
            if val is None or not str(val).strip():
                raise ValueError("Shortcuts: {} is required".format(prop))

        # Validate targetType enum
        target_type = properties.get('targetType')
        if target_type and str(target_type).upper() not in ['FILESYSTEM', 'URL', 'SHELL']:
            raise ValueError("targetType must be one of: FILESYSTEM, URL, SHELL")

        # Validate action enum if present
        action = properties.get('action')
        if action and action.upper() not in self.VALID_ACTIONS:
            raise ValueError("action must be one of: {}".format(', '.join(self.VALID_ACTIONS)))

        # Validate shortcutKey as xs:unsignedByte (0-255) if present
        shortcut_key = properties.get('shortcutKey')
        if shortcut_key is not None:
            try:
                num = int(shortcut_key)
                if num < 0 or num > 255:
                    raise ValueError("shortcutKey must be between 0 and 255")
            except (ValueError, TypeError):
                raise ValueError("shortcutKey must be an integer between 0 and 255")

        # Validate boolean property 'disabled' (xs:boolean)
        disabled = properties.get('disabled')
        if disabled is not None:
            if isinstance(disabled, str):
                if disabled.lower() not in ['true', 'false', '0', '1']:
                    raise ValueError("disabled must be boolean or 'true'/'false'")
            elif not isinstance(disabled, bool):
                raise ValueError("disabled must be boolean")

    def _validate_network_shares_properties(self, properties):
        """Validate NetworkShares properties"""
        # Check required properties
        for prop in ['name', 'path', 'comment']:
            val = properties.get(prop)
            if val is None or not str(val).strip():
                raise ValueError("NetworkShares: {} is required".format(prop))

        # Validate action enum if present
        action = properties.get('action')
        if action and action.upper() not in self.VALID_ACTIONS:
            raise ValueError("action must be one of: {}".format(', '.join(self.VALID_ACTIONS)))

        # Validate boolean properties (xs:boolean)
        bool_props = ['allRegular', 'allHidden', 'allAdminDrive', 'disabled']
        for prop in bool_props:
            val = properties.get(prop)
            if val is not None:
                if isinstance(val, str):
                    if val.lower() not in ['true', 'false', '0', '1']:
                        raise ValueError("{} must be boolean or 'true'/'false'".format(prop))
                elif not isinstance(val, bool):
                    raise ValueError("{} must be boolean".format(prop))

        # Validate userLimit as xs:unsignedByte (0-255) if present
        user_limit = properties.get('userLimit')
        if user_limit is not None:
            try:
                num = int(user_limit)
                if num < 0 or num > 255:
                    raise ValueError("userLimit must be between 0 and 255")
            except (ValueError, TypeError):
                raise ValueError("userLimit must be an integer between 0 and 255")

        # Validate limitUsers enum if present
        limit_users = properties.get('limitUsers')
        if limit_users and limit_users.upper() not in ['SET_LIMIT', 'MAX_ALLOWED', 'NO_CHANGE']:
            raise ValueError("limitUsers must be one of: SET_LIMIT, MAX_ALLOWED, NO_CHANGE")

        # Validate abe enum if present
        abe = properties.get('abe')
        if abe and abe.upper() not in ['ENABLE', 'DISABLE', 'NO_CHANGE']:
            raise ValueError("abe must be one of: ENABLE, DISABLE, NO_CHANGE")

    def _validate_printers_properties(self, properties):
        """Validate Printers properties"""
        # Check required properties
        for prop in ['path', 'port']:
            val = properties.get(prop)
            if val is None or not str(val).strip():
                raise ValueError("Printers: {} is required".format(prop))

        # Validate action enum if present
        action = properties.get('action')
        if action and action.upper() not in self.VALID_ACTIONS:
            raise ValueError("action must be one of: {}".format(', '.join(self.VALID_ACTIONS)))

        # Validate boolean properties (xs:boolean)
        bool_props = ['default', 'skipLocal', 'deleteAll', 'persistent', 'deleteMaps', 'disabled']
        for prop in bool_props:
            val = properties.get(prop)
            if val is not None:
                if isinstance(val, str):
                    if val.lower() not in ['true', 'false', '0', '1']:
                        raise ValueError("{} must be boolean or 'true'/'false'".format(prop))
                elif not isinstance(val, bool):
                    raise ValueError("{} must be boolean".format(prop))

    def _validate_scheduled_tasks_properties(self, properties):
        """Validate ScheduledTasks properties"""
        # Check required properties
        for prop in ['name', 'appName', 'enabled']:
            val = properties.get(prop)
            if val is None or not str(val).strip():
                raise ValueError("ScheduledTasks: {} is required".format(prop))

        # Validate action enum if present
        action = properties.get('action')
        if action and action.upper() not in self.VALID_ACTIONS:
            raise ValueError("action must be one of: {}".format(', '.join(self.VALID_ACTIONS)))

        # Validate boolean properties (xs:boolean)
        bool_props = ['enabled', 'deleteWhenDone', 'startOnlyIfIdle', 'stopOnIdleEnd', 'noStartIfOnBatteries', 'stopIfGoingOnBatteries', 'systemRequired', 'disabled']
        for prop in bool_props:
            val = properties.get(prop)
            if val is not None:
                if isinstance(val, str):
                    if val.lower() not in ['true', 'false', '0', '1']:
                        raise ValueError("{} must be boolean or 'true'/'false'".format(prop))
                elif not isinstance(val, bool):
                    raise ValueError("{} must be boolean".format(prop))

        # Validate maxRunTime and deadlineMinutes as unsigned int (0-4294967295) if present
        unsigned_int_props = ['maxRunTime', 'deadlineMinutes']
        for prop in unsigned_int_props:
            val = properties.get(prop)
            if val is not None:
                try:
                    num = int(val)
                    if num < 0 or num > 4294967295:
                        raise ValueError("{} must be between 0 and 4294967295".format(prop))
                except (ValueError, TypeError):
                    raise ValueError("{} must be an integer between 0 and 4294967295".format(prop))

    def _validate_services_properties(self, properties):
        """Validate Services properties"""
        # Check required property
        service_name = properties.get('serviceName')
        if service_name is None or not str(service_name).strip():
            raise ValueError("Services: serviceName is required")

        # Validate action enum if present
        action = properties.get('action')
        if action and action.upper() not in self.VALID_ACTIONS:
            raise ValueError("action must be one of: {}".format(', '.join(self.VALID_ACTIONS)))

        # Validate boolean property 'disabled' (xs:boolean)
        disabled = properties.get('disabled')
        if disabled is not None:
            if isinstance(disabled, str):
                if disabled.lower() not in ['true', 'false', '0', '1']:
                    raise ValueError("disabled must be boolean or 'true'/'false'")
            elif not isinstance(disabled, bool):
                raise ValueError("disabled must be boolean")

    def _validate_drives_properties(self, properties):
        """Validate Drives properties"""
        # Check required properties
        for prop in ['path', 'persistent', 'useLetter', 'letter']:
            val = properties.get(prop)
            if val is None or not str(val).strip():
                raise ValueError("Drives: {} is required".format(prop))

        # Validate action enum if present
        action = properties.get('action')
        if action and action.upper() not in self.VALID_ACTIONS:
            raise ValueError("action must be one of: {}".format(', '.join(self.VALID_ACTIONS)))

        # Validate letter is a single character A-Z (case insensitive)
        letter = properties.get('letter')
        if letter is not None:
            stripped = str(letter).strip()
            if not stripped.isalpha() or len(stripped) != 1:
                raise ValueError("letter must be a single letter A-Z")

        # Validate persistent, useLetter, disabled as xs:unsignedByte (0-255)
        unsigned_byte_props = ['persistent', 'useLetter', 'disabled']
        for prop in unsigned_byte_props:
            val = properties.get(prop)
            if val is not None:
                try:
                    num = int(val)
                    if num < 0 or num > 255:
                        raise ValueError("{} must be between 0 and 255".format(prop))
                except (ValueError, TypeError):
                    raise ValueError("{} must be an integer between 0 and 255".format(prop))

        # Validate thisDrive and allDrives enums if present
        for prop in ['thisDrive', 'allDrives']:
            val = properties.get(prop)
            if val and val.upper() not in ['NOCHANGE', 'HIDE', 'SHOW']:
                raise ValueError("{} must be one of: NOCHANGE, HIDE, SHOW".format(prop))

    def _validate_inifiles_properties(self, properties):
        """Validate IniFiles properties"""
        # Check required property
        path = properties.get('path')
        if path is None or not str(path).strip():
            raise ValueError("IniFiles: path is required")

        # Validate action enum if present
        action = properties.get('action')
        if action and action.upper() not in self.VALID_ACTIONS:
            raise ValueError("action must be one of: {}".format(', '.join(self.VALID_ACTIONS)))

        # Validate disabled as xs:unsignedByte (0-255) if present
        disabled = properties.get('disabled')
        if disabled is not None:
            try:
                num = int(disabled)
                if num < 0 or num > 255:
                    raise ValueError("disabled must be between 0 and 255")
            except (ValueError, TypeError):
                raise ValueError("disabled must be an integer between 0 and 255")

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
                raise ValueError("Invalid UID format: {}".format(uid))
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
            logger.error("Failed to encrypt password: {}".format(e))
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

        # Get allowed properties for this type
        schema = self.PROPERTY_SCHEMAS[pref_type]
        allowed = set(schema['required'] + schema['optional'])

        for key, value in properties.items():
            if key not in allowed:
                # Skip unknown properties (should have been validated)
                continue
            if value is None:
                continue
            # Skip SubProp and Triggers - handle as child elements
            if key in ['SubProp', 'Triggers']:
                continue
            if isinstance(value, bool):
                props_elem.set(key, self._bool_to_int(value))
            else:
                props_elem.set(key, str(value))

        # Handle nested SubProp elements for Registry
        if pref_type == 'Registry' and 'SubProp' in properties:
            for subprop in properties['SubProp']:
                subprop_elem = self._create_subprop_element(subprop)
                props_elem.append(subprop_elem)

        # Handle nested Triggers for ScheduledTasks
        if pref_type == 'ScheduledTasks' and 'Triggers' in properties:
            triggers_elem = self._create_triggers_element(properties['Triggers'])
            props_elem.append(triggers_elem)

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

            cond_elem = ET.Element('Filter{}'.format(cond_type))
            for key, value in condition.items():
                if key == 'type':
                    continue
                if isinstance(value, bool):
                    cond_elem.set(key, self._bool_to_int(value))
                else:
                    cond_elem.set(key, str(value))
            filters_elem.append(cond_elem)

        return filters_elem

    def _create_subprop_element(self, subprop):
        """Create <SubProp> element for Registry bitfield operations"""
        elem = ET.Element('SubProp')
        for attr in ['id', 'value', 'mask']:
            if attr in subprop:
                elem.set(attr, str(subprop[attr]))
        return elem

    def _create_triggers_element(self, triggers):
        """Create <Triggers> element for ScheduledTasks"""
        triggers_elem = ET.Element('Triggers')
        for trigger in triggers:
            trigger_elem = ET.Element('Trigger')
            for key, value in trigger.items():
                if isinstance(value, bool):
                    trigger_elem.set(key, self._bool_to_int(value))
                else:
                    trigger_elem.set(key, str(value))
            triggers_elem.append(trigger_elem)
        return triggers_elem

    def _create_preference_element(self, pref):
        """
        Create XML element for a single preference

        Args:
            pref: preference dict

        Returns:
            ET.Element for the preference
        """
        pref_type = pref['type']
        clsid = self.INNER_CLSID_MAP[pref_type]

        # Create root element for this preference
        pref_elem = ET.Element(pref_type)
        pref_elem.set('clsid', clsid)
        pref_elem.set('name', pref.get('name', ''))
        pref_elem.set('uid', pref['uid'])
        pref_elem.set('changed', pref['changed'])

        # Optional common attributes
        if 'desc' in pref:
            pref_elem.set('desc', str(pref['desc']))
        if 'status' in pref:
            pref_elem.set('status', str(pref['status']))
        if 'image' in pref:
            pref_elem.set('image', str(pref['image']))

        # Boolean common attributes (convert to '0'/'1')
        for attr in ['bypassErrors', 'userContext', 'removePolicy']:
            if attr in pref:
                value = pref[attr]
                # Special handling for userContext string 'User'/'Machine'
                if attr == 'userContext' and isinstance(value, str):
                    if value.lower() == 'user':
                        value = True
                    elif value.lower() == 'machine':
                        value = False
                    # else treat as boolean via _bool_to_int
                pref_elem.set(attr, self._bool_to_int(value))

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

                    logger.info("Saved {} {} preferences to {}".format(len(prefs), pref_type, xml_path))

                except Exception as e:
                    error_msg = "Failed to save {} preferences: {}".format(pref_type, str(e))
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    errors.append(error_msg)

            if errors:
                return {
                    'success': False,
                    'message': "Partial success with errors: {}".format('; '.join(errors)),
                    'files': saved_files,
                    'errors': errors
                }

            return {
                'success': True,
                'message': "Successfully saved preferences to {} file(s)".format(len(saved_files)),
                'files': saved_files
            }

        except Exception as e:
            logger.error("Failed to save preferences: {}".format(e))
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
        if os.path.exists(xml_path):
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                if root.tag == 'Collection':
                    return root
                else:
                    logger.warning("Root element is not Collection in {}, creating new".format(xml_path))
            except ET.ParseError as e:
                logger.warning("Failed to parse XML file {}: {}, creating new".format(xml_path, e))

        # Create new Collection
        clsid = self.OUTER_CLSID_MAP[pref_type]
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
            types_to_read = self.OUTER_CLSID_MAP.keys()

        for ptype in types_to_read:
            try:
                xml_path = self._get_xml_file_path(gpo_guid, scope, ptype)
                if not xml_path.exists():
                    continue

                tree = ET.parse(xml_path)
                collection = tree.getroot()
                if collection.tag != 'Collection':
                    logger.warning("Root element is not Collection in {}".format(xml_path))
                    continue

                preferences = []
                for pref_elem in collection.findall('*'):
                    pref = self._parse_preference_element(pref_elem)
                    preferences.append(pref)

                result[ptype] = preferences

            except Exception as e:
                logger.error("Failed to read {} preferences: {}".format(ptype, e))

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
            'status': pref_elem.get('status', ''),
            'image': pref_elem.get('image', ''),
            'desc': pref_elem.get('desc', ''),
        }

        # Handle boolean attributes with special handling for userContext
        bypass_errors_val = pref_elem.get('bypassErrors', '0')
        pref['bypassErrors'] = bypass_errors_val == '1'

        user_context_val = pref_elem.get('userContext', '0')
        if user_context_val.lower() == 'user':
            pref['userContext'] = True
        elif user_context_val.lower() == 'machine':
            pref['userContext'] = False
        else:
            pref['userContext'] = user_context_val == '1'

        remove_policy_val = pref_elem.get('removePolicy', '0')
        pref['removePolicy'] = remove_policy_val == '1'

        # Convert numeric attributes
        for attr in ('image', 'status'):
            if pref[attr].isdigit():
                pref[attr] = int(pref[attr])

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

            # Parse child elements for specific types
            if pref['type'] == 'Registry':
                subprops = []
                for subprop_elem in props_elem.findall('SubProp'):
                    subprop = {}
                    for attr in ['id', 'value', 'mask']:
                        val = subprop_elem.get(attr)
                        if val is not None:
                            if val.isdigit():
                                subprop[attr] = int(val)
                            else:
                                subprop[attr] = val
                    if subprop:
                        subprops.append(subprop)
                if subprops:
                    properties['SubProp'] = subprops

            elif pref['type'] == 'ScheduledTasks':
                triggers = []
                for trigger_elem in props_elem.findall('Triggers/Trigger'):
                    trigger = {}
                    for key, value in trigger_elem.items():
                        if value.isdigit():
                            trigger[key] = int(value)
                        elif value.lower() in ('true', 'false'):
                            trigger[key] = value.lower() == 'true'
                        else:
                            trigger[key] = value
                    if trigger:
                        triggers.append(trigger)
                if triggers:
                    properties['Triggers'] = triggers

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
                logger.debug("XML file not found: {}".format(xml_path))
                return False

            tree = ET.parse(xml_path)
            collection = tree.getroot()
            if collection.tag != 'Collection':
                logger.warning("Root element is not Collection in {}".format(xml_path))
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
                    logger.info("Deleted empty XML file: {}".format(xml_path))
                else:
                    xml_content = self._pretty_xml(collection)
                    xml_path.write_text(xml_content, encoding='utf-8')
                    logger.info("Deleted preference {} from {}".format(uid, xml_path))
                return True
            else:
                logger.debug("Preference with UID {} not found in {}".format(uid, xml_path))
                return False

        except Exception as e:
            logger.error("Failed to delete preference: {}".format(e))
            logger.error(traceback.format_exc())
            return False