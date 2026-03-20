#!/usr/bin/env python3
#
# update_paths.py - Update GPUIService paths via GSettings and systemd drop-in
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

import os
import sys
import logging
import tempfile
import json
import time
import argparse
from pathlib import Path

import dbus
from gi.repository import Gio

logger = logging.getLogger('gpuiservice')

class PathsUpdater:
    """Update GPUIService paths via GSettings and systemd drop-in with rollback"""

    SYSTEMD_SERVICE = 'gpuiservice.service'
    SYSTEMD_DROPIN_DIR = '/etc/systemd/system/gpuiservice.service.d'
    DROPIN_FILENAME = 'paths-override.conf'
    GSETTINGS_SCHEMA = 'org.altlinux.gpuiservice'

    def __init__(self):
        self.settings = None
        self.systemd = None
        self.backup_file = None
        self.backup_data = {}

    def connect_to_systemd(self):
        """Connect to systemd DBus interface"""
        try:
            bus = dbus.SystemBus()
            systemd = bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
            self.systemd = dbus.Interface(systemd, 'org.freedesktop.systemd1.Manager')
            logger.debug("Connected to systemd DBus interface")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to systemd DBus: {e}")
            return False

    def connect_to_gsettings(self):
        """Connect to GSettings"""
        try:
            self.settings = Gio.Settings.new(self.GSETTINGS_SCHEMA)
            logger.debug("Connected to GSettings")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to GSettings: {e}")
            return False

    def backup_current_values(self):
        """Backup current GSettings values and drop-in file"""
        if not self.settings:
            return False

        try:
            self.backup_data = {
                'monitor_path': self.settings.get_string('monitor-path'),
                'sysvol_path': self.settings.get_string('sysvol-path'),
                'dropin_exists': False,
                'dropin_content': None
            }

            dropin_path = Path(self.SYSTEMD_DROPIN_DIR) / self.DROPIN_FILENAME
            if dropin_path.exists():
                self.backup_data['dropin_exists'] = True
                self.backup_data['dropin_content'] = dropin_path.read_text()

            # Create backup file
            fd, self.backup_file = tempfile.mkstemp(prefix='gpuiservice-paths-backup-', suffix='.json')
            os.close(fd)
            with open(self.backup_file, 'w') as f:
                json.dump(self.backup_data, f)

            logger.info(f"Backup created at {self.backup_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup current values: {e}")
            return False

    def update_gsettings(self, monitor_path=None, sysvol_path=None):
        """Update GSettings keys"""
        if not self.settings:
            return False

        try:
            if monitor_path is not None:
                self.settings.set_string('monitor-path', monitor_path)
                logger.info(f"Updated monitor-path to: {monitor_path}")

            if sysvol_path is not None:
                self.settings.set_string('sysvol-path', sysvol_path)
                logger.info(f"Updated sysvol-path to: {sysvol_path}")

            # Ensure changes are written immediately
            self.settings.sync()
            return True
        except Exception as e:
            logger.error(f"Failed to update GSettings: {e}")
            return False

    def create_dropin_override(self, monitor_path=None, sysvol_path=None):
        """Create systemd drop-in override with new paths"""
        try:
            dropin_dir = Path(self.SYSTEMD_DROPIN_DIR)
            dropin_dir.mkdir(parents=True, exist_ok=True)

            dropin_path = dropin_dir / self.DROPIN_FILENAME
            lines = ['[Service]']

            if monitor_path:
                # Ensure path exists
                Path(monitor_path).mkdir(parents=True, exist_ok=True)
                lines.append(f'ReadOnlyPaths={monitor_path}')

            if sysvol_path:
                # Ensure path exists
                Path(sysvol_path).mkdir(parents=True, exist_ok=True)
                lines.append(f'ReadWritePaths={sysvol_path}')

            dropin_path.write_text('\n'.join(lines) + '\n')
            logger.info(f"Created drop-in override at {dropin_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create drop-in override: {e}")
            return False

    def restart_service(self):
        """Restart GPUIService via systemd DBus with monitoring"""
        if not self.systemd:
            return False

        try:
            # Get current service state
            service_path = self.systemd.GetUnit(self.SYSTEMD_SERVICE)
            service_obj = dbus.SystemBus().get_object('org.freedesktop.systemd1', service_path)
            service_iface = dbus.Interface(service_obj, 'org.freedesktop.systemd1.Unit')

            # Stop service
            logger.info(f"Stopping {self.SYSTEMD_SERVICE}...")
            job = self.systemd.StopUnit(self.SYSTEMD_SERVICE, 'replace')

            # Wait for stop
            time.sleep(2)

            # Reload systemd to pick up drop-in changes
            self.systemd.Reload()
            logger.debug("Systemd configuration reloaded")

            # Start service
            logger.info(f"Starting {self.SYSTEMD_SERVICE}...")
            job = self.systemd.StartUnit(self.SYSTEMD_SERVICE, 'replace')

            # Monitor startup (simplified - wait and check active state)
            time.sleep(3)

            # Check service state
            service_state = service_iface.get('org.freedesktop.systemd1.Unit', 'ActiveState')
            if service_state == 'active':
                logger.info(f"Service {self.SYSTEMD_SERVICE} restarted successfully")
                return True
            else:
                logger.error(f"Service {self.SYSTEMD_SERVICE} failed to start, state: {service_state}")
                return False

        except dbus.exceptions.DBusException as e:
            logger.error(f"DBus error during service restart: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to restart service: {e}")
            return False

    def rollback(self):
        """Rollback to backed-up values"""
        if not self.backup_file or not os.path.exists(self.backup_file):
            logger.error("No backup file found for rollback")
            return False

        try:
            with open(self.backup_file, 'r') as f:
                backup = json.load(f)

            # Restore GSettings
            if self.settings:
                if 'monitor_path' in backup:
                    self.settings.set_string('monitor-path', backup['monitor_path'])
                if 'sysvol_path' in backup:
                    self.settings.set_string('sysvol-path', backup['sysvol_path'])
                self.settings.sync()
                logger.info("Restored GSettings from backup")

            # Restore or remove drop-in file
            dropin_path = Path(self.SYSTEMD_DROPIN_DIR) / self.DROPIN_FILENAME
            if backup.get('dropin_exists'):
                dropin_path.write_text(backup['dropin_content'])
                logger.info(f"Restored drop-in file {dropin_path}")
            elif dropin_path.exists():
                dropin_path.unlink()
                logger.info(f"Removed drop-in file {dropin_path}")

            # Remove backup file
            os.unlink(self.backup_file)
            self.backup_file = None
            logger.info("Rollback completed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed during rollback: {e}")
            return False

    def cleanup_backup(self):
        """Clean up backup file if it exists"""
        if self.backup_file and os.path.exists(self.backup_file):
            try:
                os.unlink(self.backup_file)
                logger.debug(f"Cleaned up backup file {self.backup_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up backup file: {e}")

    def update_paths(self, monitor_path=None, sysvol_path=None):
        """Main method to update paths with rollback on failure"""
        if not monitor_path and not sysvol_path:
            logger.error("At least one path must be specified")
            return False

        # Validate paths
        if monitor_path and not self._validate_monitor_path(monitor_path):
            return False
        if sysvol_path and not self._validate_sysvol_path(sysvol_path):
            return False

        # Connect to services
        if not self.connect_to_gsettings():
            return False
        if not self.connect_to_systemd():
            return False

        # Backup current state
        if not self.backup_current_values():
            return False

        try:
            # Update GSettings
            if not self.update_gsettings(monitor_path, sysvol_path):
                raise Exception("Failed to update GSettings")

            # Create drop-in override
            if not self.create_dropin_override(monitor_path, sysvol_path):
                raise Exception("Failed to create drop-in override")

            # Restart service
            if not self.restart_service():
                raise Exception("Service restart failed")

            # Success - clean up backup
            self.cleanup_backup()
            logger.info("Paths updated successfully")
            return True

        except Exception as e:
            logger.error(f"Update failed: {e}")
            logger.info("Initiating rollback...")
            if not self.rollback():
                logger.error("Rollback also failed! Manual intervention required.")
                return False

            # Try to restart with original configuration
            logger.info("Attempting to restart service with original configuration...")
            if not self.restart_service():
                logger.error("Failed to restart service after rollback")
                return False

            logger.info("Rollback completed, service restored")
            return False

    def _validate_monitor_path(self, path):
        """Validate monitor path (ADMX definitions directory)"""
        if not os.path.isabs(path):
            logger.error(f"Monitor path must be absolute: {path}")
            return False

        # Check if directory exists or can be created
        parent = os.path.dirname(path)
        if not os.path.exists(parent):
            logger.error(f"Parent directory does not exist: {parent}")
            return False

        if not os.access(parent, os.W_OK):
            logger.error(f"No write permission to create directory: {parent}")
            return False

        return True

    def _validate_sysvol_path(self, path):
        """Validate sysvol path (FreeIPA GPT storage)"""
        if not os.path.isabs(path):
            logger.error(f"Sysvol path must be absolute: {path}")
            return False

        # Check if directory exists or can be created
        parent = os.path.dirname(path)
        if not os.path.exists(parent):
            logger.error(f"Parent directory does not exist: {parent}")
            return False

        if not os.access(parent, os.W_OK):
            logger.error(f"No write permission to create directory: {parent}")
            return False

        return True

def main():
    parser = argparse.ArgumentParser(
        description='Update GPUIService paths via GSettings and systemd drop-in'
    )
    parser.add_argument('--monitor-path', help='ADMX policy definitions directory')
    parser.add_argument('--sysvol-path', help='FreeIPA sysvol directory')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    if not args.monitor_path and not args.sysvol_path:
        parser.error("At least one of --monitor-path or --sysvol-path must be specified")

    # Setup logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    updater = PathsUpdater()
    success = updater.update_paths(args.monitor_path, args.sysvol_path)

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()