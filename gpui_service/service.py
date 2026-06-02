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
GPUIService - DBus service for GPO editing functionality
"""

import dbus
import dbus.service
import logging
import json
import subprocess

logger = logging.getLogger('gpuiservice')

class GPUIService(dbus.service.Object):
    """
    DBus service for GPO editing functionality
    Uses ADMX policy definitions to generate and manage GPT structures
    Provides API for editing existing GPO parameters without creating new policy objects
    Analog of gpedit.msc for Linux infrastructure based on FreeIPA
    """

    def __init__(self, bus_name, object_path, data_store_dict):
        super().__init__(bus_name, object_path)
        self.data_store = data_store_dict
        logger.info(f"GPUIService initialized at {object_path}")

    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Introspectable',
                         out_signature='s',
                         connection_keyword='connection')
    def Introspect(self, connection=None):
        """
        Provide introspection data for DBus clients
        Required for clients to discover methods and interfaces
        """
        return """<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
                "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
                <node name="/org/altlinux/gpuiservice">
                <interface name="org.altlinux.GPUIService">
                    <method name="get">
                    <arg name="path" direction="in" type="s"/>
                    <arg name="value" direction="out" type="v"/>
                    </method>
                    <method name="set">
                    <arg name="name_gpt" direction="in" type="s"/>
                    <arg name="target" direction="in" type="s"/>
                    <arg name="path" direction="in" type="s"/>
                    <arg name="value" direction="in" type="s"/>
                    <arg name="metadata" direction="in" type="s"/>
                    <arg name="success" direction="out" type="b"/>
                    </method>
                    <method name="list_children">
                    <arg name="parent_path" direction="in" type="s"/>
                    <arg name="children" direction="out" type="v"/>
                    </method>
                    <method name="find">
                    <arg name="search_pattern" direction="in" type="s"/>
                    <arg name="search_type" direction="in" type="s"/>
                    <arg name="results" direction="out" type="v"/>
                    </method>
                    <method name="get_current_value">
                    <arg name="name_gpt" direction="in" type="s"/>
                    <arg name="target" direction="in" type="s"/>
                    <arg name="path" direction="in" type="s"/>
                    <arg name="results" direction="out" type="v"/>
                    </method>
                    <method name="delete_policy_value">
                    <arg name="name_gpt" direction="in" type="s"/>
                    <arg name="target" direction="in" type="s"/>
                    <arg name="path" direction="in" type="s"/>
                    <arg name="success" direction="out" type="b"/>
                    </method>
                    <method name="reload">
                    <arg name="success" direction="out" type="b"/>
                    </method>
                    <method name="save_preference">
                    <arg name="name_gpt" direction="in" type="s"/>
                    <arg name="target" direction="in" type="s"/>
                    <arg name="pref_type" direction="in" type="s"/>
                    <arg name="value" direction="in" type="s"/>
                    <arg name="uid" direction="in" type="s"/>
                    <arg name="result" direction="out" type="v"/>
                    </method>
                    <method name="get_preferences">
                    <arg name="gpo_guid" direction="in" type="s"/>
                    <arg name="scope" direction="in" type="s"/>
                    <arg name="pref_type" direction="in" type="s"/>
                    <arg name="result" direction="out" type="v"/>
                    </method>
                    <method name="delete_preference">
                    <arg name="gpo_guid" direction="in" type="s"/>
                    <arg name="scope" direction="in" type="s"/>
                    <arg name="pref_type" direction="in" type="s"/>
                    <arg name="uid" direction="in" type="s"/>
                    <arg name="success" direction="out" type="b"/>
                    </method>
                    <method name="update_paths">
                    <arg name="monitor_path" direction="in" type="s"/>
                    <arg name="sysvol_path" direction="in" type="s"/>
                    <arg name="success" direction="out" type="b"/>
                    </method>
                    <method name="set_locale">
                    <arg name="locale" direction="in" type="s"/>
                    <arg name="success" direction="out" type="b"/>
                    </method>
                    <method name="get_locale">
                    <arg name="locale" direction="out" type="s"/>
                    </method>
                    <method name="get_policy_state">
                    <arg name="name_gpt" direction="in" type="s"/>
                    <arg name="target" direction="in" type="s"/>
                    <arg name="policy_path" direction="in" type="s"/>
                    <arg name="result" direction="out" type="v"/>
                    </method>
                    <method name="set_policy_state">
                    <arg name="name_gpt" direction="in" type="s"/>
                    <arg name="target" direction="in" type="s"/>
                    <arg name="policy_path" direction="in" type="s"/>
                    <arg name="state" direction="in" type="s"/>
                    <arg name="success" direction="out" type="b"/>
                    </method>
                    <method name="get_scripts">
                    <arg name="name_gpt" direction="in" type="s"/>
                    <arg name="target" direction="in" type="s"/>
                    <arg name="script_type" direction="in" type="s"/>
                    <arg name="result" direction="out" type="v"/>
                    </method>
                    <method name="set_scripts">
                    <arg name="name_gpt" direction="in" type="s"/>
                    <arg name="target" direction="in" type="s"/>
                    <arg name="script_type" direction="in" type="s"/>
                    <arg name="scripts_json" direction="in" type="s"/>
                    <arg name="success" direction="out" type="b"/>
                    </method>
                    <method name="get_comments">
                    <arg name="name_gpt" direction="in" type="s"/>
                    <arg name="target" direction="in" type="s"/>
                    <arg name="locale" direction="in" type="s"/>
                    <arg name="result" direction="out" type="v"/>
                    </method>
                    <method name="save_comment">
                    <arg name="name_gpt" direction="in" type="s"/>
                    <arg name="target" direction="in" type="s"/>
                    <arg name="policy_ref" direction="in" type="s"/>
                    <arg name="comment_text" direction="in" type="s"/>
                    <arg name="namespace" direction="in" type="s"/>
                    <arg name="success" direction="out" type="b"/>
                    </method>
                    <method name="delete_comment">
                    <arg name="name_gpt" direction="in" type="s"/>
                    <arg name="target" direction="in" type="s"/>
                    <arg name="policy_ref" direction="in" type="s"/>
                    <arg name="success" direction="out" type="b"/>
                    </method>
                    <signal name="locale_changed">
                    <arg name="locale" type="s"/>
                    </signal>
                </interface>
                <interface name="org.freedesktop.DBus.Introspectable">
                    <method name="Introspect">
                    <arg name="data" direction="out" type="s"/>
                    </method>
                </interface>
                <interface name="org.freedesktop.DBus.Properties">
                    <method name="Get">
                    <arg name="interface" direction="in" type="s"/>
                    <arg name="property" direction="in" type="s"/>
                    <arg name="value" direction="out" type="v"/>
                    </method>
                    <method name="Set">
                    <arg name="interface" direction="in" type="s"/>
                    <arg name="property" direction="in" type="s"/>
                    <arg name="value" direction="in" type="v"/>
                    </method>
                    <method name="GetAll">
                    <arg name="interface" direction="in" type="s"/>
                    <arg name="properties" direction="out" type="a{sv}"/>
                    </method>
                </interface>
                </node>"""

    @dbus.service.method('org.altlinux.GPUIService', in_signature='s', out_signature='v')
    def get(self, path):
        """
        Get parameter value from GPO
        Args:
            path: Path to the parameter in GPO structure
        Returns:
            Value of the parameter as JSON string for complex types
        """
        logger.info(f"get method called with path: {path}")
        value = self.data_store.get(path)
        if value is None:
            return ""

        if isinstance(value, (dict, list, tuple, set)):
            return json.dumps(value, default=str, ensure_ascii=False)
        elif isinstance(value, (int, float, bool)):
            return value
        else:
            return str(value)

    @dbus.service.method('org.altlinux.GPUIService', in_signature='sssss', out_signature='b')
    def set(self, name_gpt, target, path, value, metadata):
        """
        Set parameter value in GPO
        Args:
            path: Path to the parameter in GPO structure (registry key)
            name_gpt: GPO path (relative to sysvol)
            target: Policy type ('Machine' or 'User'), empty string for default
            value: Value to set
            metadata: ADMX metadata path (optional, empty string to extract from value)
        Returns:
            True if successful, False otherwise
        """
        val_log = value if len(str(value)) <= 100 else str(value)[:100] + '...'
        logger.info(f"set method called with path: {path}, name_gpt: {name_gpt}, target: {target}, value: {val_log}, metadata: {metadata}")
        # Convert empty target to None (use defaults)
        target_param = target if target else None
        return self.data_store.set(path, value, name_gpt, target_param, metadata)

    @dbus.service.method('org.altlinux.GPUIService', in_signature='s', out_signature='v')
    def list_children(self, parent_path):
        """
        List child parameters under a parent path
        Args:
            parent_path: Parent path in GPO structure
        Returns:
            Array of child parameter paths as JSON string
        """
        logger.info(f"list_children method called with parent_path: {parent_path}")
        result = self.data_store.list_children(parent_path)
        if isinstance(result, (dict, list, tuple, set)):
            return json.dumps(result, default=str, ensure_ascii=False)
        elif isinstance(result, (int, float, bool)):
            return result
        else:
            return str(result)


    @dbus.service.method('org.altlinux.GPUIService', in_signature='ss', out_signature='v')
    def find(self, search_pattern, search_type):
        """
        Find parameters matching search criteria
        Args:
            search_pattern: Pattern to search for
            search_type: Type of search (name, value, category, etc.)
        Returns:
            Array of matching parameter paths as JSON string
        """
        logger.info(f"find method called with pattern: {search_pattern}, type: {search_type}")
        result = self.data_store.find(search_pattern, search_type or 'all')
        return json.dumps(result, ensure_ascii=False)

    @dbus.service.method('org.altlinux.GPUIService', in_signature='sss', out_signature='v')
    def get_current_value(self, name_gpt, target, path):
        """
        Get current value from GPO policy file
        Args:
            name_gpt: GPO path (relative to sysvol)
            target: Policy type ('Machine' or 'User'), empty string for default
            path: Registry key path (e.g., 'Software\\BaseALT\\Policies\\GPUpdate')
        Returns:
            JSON string with value_data and value_type if found, empty string otherwise
        """
        logger.info(f"get_current_value method called with name_gpt: {name_gpt}, target: {target}, path: {path}")
        try:
            # Convert empty target to None (use defaults)
            target_param = target if target else None

            result = self.data_store.get_current_value(path, name_gpt, target_param)
            if result is None:
                return ""

            # result is tuple (value_data, value_type)
            value_data, value_type = result
            response = {
                "value_data": value_data,
                "value_type": value_type
            }
            return json.dumps(response, default=str, ensure_ascii=False)
        except (OSError, IOError) as e:
            logger.error("I/O error in get_current_value: %s", e)
            return ""
        except Exception as e:
            logger.exception("Unexpected error in get_current_value: %s", e)
            return ""

    @dbus.service.method('org.altlinux.GPUIService', in_signature='sss', out_signature='b')
    def delete_policy_value(self, name_gpt, target, path):
        """
        Delete a policy value from GPO Registry.pol file
        Args:
            name_gpt: GPO path (relative to sysvol)
            target: Policy type ('Machine' or 'User'), empty string for default
            path: Registry key path (e.g., 'Software\\BaseALT\\Policies\\GPUpdate\\SettingName')
        Returns:
            True if deleted (or value didn't exist), False on error
        """
        logger.info(f"delete_policy_value method called with name_gpt: {name_gpt}, target: {target}, path: {path}")
        try:
            target_param = target if target else None
            return self.data_store.delete_policy_value(path, name_gpt, target_param)
        except (OSError, IOError) as e:
            logger.error("I/O error in delete_policy_value: %s", e)
            return False
        except Exception as e:
            logger.exception("Unexpected error in delete_policy_value: %s", e)
            return False

    @dbus.service.method('org.altlinux.GPUIService', out_signature='b')
    def reload(self):
        """
        Manually trigger reload of ADMX data for GPO generation.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Manual reload requested")
        if self.data_store.monitor_path:
            try:
                try:
                    from .parse_admx_structure import AdmxParser
                except ImportError:
                    from parse_admx_structure import AdmxParser
                AdmxParser.clear_cache()
                self.data_store.load_from_directory(
                    self.data_store.monitor_path,
                    self.data_store.locale
                )
                logger.info("ADMX data reloaded successfully")
                return True
            except Exception as e:
                logger.exception(f"Error reloading ADMX data: {e}")
                return False
        logger.warning("No monitor path set, cannot reload")
        return False

    @dbus.service.method('org.altlinux.GPUIService', in_signature='sssss', out_signature='v')
    def save_preference(self, name_gpt, target, pref_type, value, uid):
        """
        Save a single Group Policy Preference

        Args:
            name_gpt: GPO path (relative to sysvol)
            target: 'Machine' or 'User'
            pref_type: Preference type (Files, Folders, etc., NOT Registry)
            value: JSON string with type-specific properties
            uid: UID of existing preference to update, empty string to create new

        Returns:
            dict with results as JSON string
        """
        logger.info(f"save_preference method called with name_gpt: {name_gpt}, target: {target}, pref_type: {pref_type}, uid: {uid}")
        try:
            result = self.data_store.save_preference(name_gpt, target, pref_type, value, uid)
            return json.dumps(result, default=str, ensure_ascii=False)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Data error in save_preference: {e}")
            return json.dumps({'success': False, 'message': str(e), 'uid': uid}, ensure_ascii=False)
        except Exception as e:
            logger.exception(f"Unexpected error in save_preference: {e}")
            return json.dumps({'success': False, 'message': str(e), 'uid': uid}, ensure_ascii=False)

    @dbus.service.method('org.altlinux.GPUIService', in_signature='sss', out_signature='v')
    def get_preferences(self, gpo_guid, scope, pref_type):
        """
        Read preferences from XML files

        Args:
            gpo_guid: GUID of the GPO
            scope: 'Machine' or 'User'
            pref_type: Preference type (empty string for all)

        Returns:
            dict with preferences as JSON string
        """
        logger.info(f"get_preferences method called with gpo_guid: {gpo_guid}, scope: {scope}, pref_type: {pref_type}")
        pref_type_param = pref_type if pref_type else None
        try:
            result = self.data_store.get_preferences(gpo_guid, scope, pref_type_param)
            return json.dumps(result, default=str, ensure_ascii=False)
        except (OSError, IOError) as e:
            logger.error(f"I/O error getting preferences: {e}")
            return json.dumps({}, ensure_ascii=False)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Data error in get_preferences: {e}")
            return json.dumps({}, ensure_ascii=False)
        except Exception as e:
            logger.exception(f"Unexpected error in get_preferences: {e}")
            return json.dumps({}, ensure_ascii=False)

    @dbus.service.method('org.altlinux.GPUIService', in_signature='ssss', out_signature='b')
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
        logger.info(f"delete_preference method called with gpo_guid: {gpo_guid}, scope: {scope}, pref_type: {pref_type}, uid: {uid}")
        try:
            return self.data_store.delete_preference(gpo_guid, scope, pref_type, uid)
        except (OSError, IOError) as e:
            logger.error(f"I/O error deleting preference: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error in delete_preference: {e}")
            return False

    @dbus.service.method('org.altlinux.GPUIService', in_signature='ss', out_signature='b')
    def update_paths(self, monitor_path, sysvol_path):
        """
        Update GPUIService paths (ADMX directory and sysvol directory)

        Args:
            monitor_path: ADMX policy definitions directory (empty string to keep current)
            sysvol_path: FreeIPA sysvol directory (empty string to keep current)

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"update_paths method called with monitor_path: {monitor_path}, sysvol_path: {sysvol_path}")

        # Build command
        cmd = ['ipa-gpo-update-paths']
        if monitor_path:
            cmd.extend(['--monitor-path', monitor_path])
        if sysvol_path:
            cmd.extend(['--sysvol-path', sysvol_path])

        # At least one path must be provided
        if len(cmd) == 1:
            logger.error("No paths specified")
            return False

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info("Paths updated successfully")
                return True
            else:
                logger.error(f"Failed to update paths: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error("Timeout updating paths")
            return False
        except FileNotFoundError as e:
            logger.error(f"Update paths command not found: {e}")
            return False
        except OSError as e:
            logger.error(f"I/O error updating paths: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error updating paths: {e}")
            return False

    @dbus.service.method('org.altlinux.GPUIService', in_signature='s', out_signature='b')
    def set_locale(self, locale):
        """
        Set locale for ADMX parsing and reload data.

        Args:
            locale: Locale string (e.g., 'ru-RU', 'en-US', 'ru_RU.UTF-8')

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"set_locale method called with locale: {locale}")
        success = self.data_store.set_locale(locale)
        if success:
            self.locale_changed(self.data_store.locale)
        return success

    @dbus.service.method('org.altlinux.GPUIService', out_signature='s')
    def get_locale(self):
        """
        Get current locale used for ADMX parsing.

        Returns:
            Current locale string (e.g., 'ru-RU', 'en-US')
        """
        return self.data_store.locale

    @dbus.service.method('org.altlinux.GPUIService', in_signature='sss', out_signature='v')
    def get_policy_state(self, name_gpt, target, policy_path):
        """
        Determine current policy state from Registry.pol + ADMX metadata.

        Args:
            name_gpt: GPO path (relative to sysvol)
            target: 'Machine' or 'User'
            policy_path: Path to policy in ADMX tree

        Returns:
            JSON with state and values
        """
        logger.info(f"get_policy_state called: name_gpt={name_gpt}, target={target}, path={policy_path}")
        try:
            target_param = target if target else None
            result = self.data_store.get_policy_state(policy_path, name_gpt, target_param)
            if result is None:
                return ""
            return json.dumps(result, default=str, ensure_ascii=False)
        except Exception as e:
            logger.exception(f"Error in get_policy_state: {e}")
            return ""

    @dbus.service.method('org.altlinux.GPUIService', in_signature='ssss', out_signature='b')
    def set_policy_state(self, name_gpt, target, policy_path, state):
        """
        Atomically set policy state.

        Args:
            name_gpt: GPO path (relative to sysvol)
            target: 'Machine' or 'User'
            policy_path: Path to policy in ADMX tree
            state: 'enabled', 'disabled', or 'not_configured'

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"set_policy_state called: name_gpt={name_gpt}, target={target}, path={policy_path}, state={state}")
        try:
            target_param = target if target else None
            return self.data_store.set_policy_state(policy_path, name_gpt, state, target_param)
        except Exception as e:
            logger.exception(f"Error in set_policy_state: {e}")
            return False

    @dbus.service.method('org.altlinux.GPUIService', in_signature='sss', out_signature='v')
    def get_scripts(self, name_gpt, target, script_type):
        """
        Get scripts for a GPO.

        Args:
            name_gpt: GPO path (relative to sysvol)
            target: 'Machine' or 'User'
            script_type: 'scripts' or 'psscripts'

        Returns:
            JSON {section: [{cmdLine, parameters}, ...]}
        """
        logger.info(f"get_scripts called: name_gpt={name_gpt}, target={target}, type={script_type}")
        try:
            result = self.data_store.get_scripts(name_gpt, target, script_type)
            return json.dumps(result, default=str, ensure_ascii=False)
        except Exception as e:
            logger.exception(f"Error in get_scripts: {e}")
            return "{}"

    @dbus.service.method('org.altlinux.GPUIService', in_signature='ssss', out_signature='b')
    def set_scripts(self, name_gpt, target, script_type, scripts_json):
        """
        Write scripts for a GPO.

        Args:
            name_gpt: GPO path (relative to sysvol)
            target: 'Machine' or 'User'
            script_type: 'scripts' or 'psscripts'
            scripts_json: JSON {section: [{cmdLine, parameters}, ...]}

        Returns:
            True if successful
        """
        logger.info(f"set_scripts called: name_gpt={name_gpt}, target={target}, type={script_type}")
        try:
            scripts_data = json.loads(scripts_json)
            return self.data_store.set_scripts(name_gpt, target, script_type, scripts_data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Invalid JSON in set_scripts: {e}")
            return False
        except Exception as e:
            logger.exception(f"Error in set_scripts: {e}")
            return False

    @dbus.service.method('org.altlinux.GPUIService', in_signature='sss', out_signature='v')
    def get_comments(self, name_gpt, target, locale):
        """
        Get comments for a GPO.

        Args:
            name_gpt: GPO path (relative to sysvol)
            target: 'Machine' or 'User'
            locale: Locale for CMTL lookup

        Returns:
            JSON {policy_name: comment_text}
        """
        logger.info(f"get_comments called: name_gpt={name_gpt}, target={target}, locale={locale}")
        try:
            result = self.data_store.get_comments(name_gpt, target, locale)
            return json.dumps(result, default=str, ensure_ascii=False)
        except Exception as e:
            logger.exception(f"Error in get_comments: {e}")
            return "{}"

    @dbus.service.method('org.altlinux.GPUIService', in_signature='sssss', out_signature='b')
    def save_comment(self, name_gpt, target, policy_ref, comment_text, namespace):
        """
        Add or update a comment.

        Args:
            name_gpt: GPO path (relative to sysvol)
            target: 'Machine' or 'User'
            policy_ref: Policy identifier
            comment_text: Comment text
            namespace: ADMX target namespace (empty for default)

        Returns:
            True if successful
        """
        logger.info(f"save_comment called: name_gpt={name_gpt}, target={target}, policy_ref={policy_ref}")
        try:
            ns = namespace if namespace else ''
            return self.data_store.save_comment(name_gpt, target, policy_ref, comment_text, ns)
        except Exception as e:
            logger.exception(f"Error in save_comment: {e}")
            return False

    @dbus.service.method('org.altlinux.GPUIService', in_signature='sss', out_signature='b')
    def delete_comment(self, name_gpt, target, policy_ref):
        """
        Delete a comment.

        Args:
            name_gpt: GPO path (relative to sysvol)
            target: 'Machine' or 'User'
            policy_ref: Policy name or 'ns:PolicyName'

        Returns:
            True if successful
        """
        logger.info(f"delete_comment called: name_gpt={name_gpt}, target={target}, policy_ref={policy_ref}")
        try:
            return self.data_store.delete_comment(name_gpt, target, policy_ref)
        except Exception as e:
            logger.exception(f"Error in delete_comment: {e}")
            return False

    @dbus.service.signal('org.altlinux.GPUIService')
    def locale_changed(self, locale):
        """
        Signal emitted when locale is changed.

        Args:
            locale: New locale string
        """
        logger.info(f"locale_changed signal emitted: {locale}")
