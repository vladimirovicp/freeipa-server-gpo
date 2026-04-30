#
# gpuiservice - GPT Directory Management API Service
#
# Copyright (C) 2025 BaseALT Ltd.
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
DirectoryMonitor - Monitor directory for ADMX file changes and reload data
"""

from pathlib import Path
from typing import Any, Callable, Optional

from gi.repository import Gio, GLib
import logging

try:
    from .config import get_monitor_path
except ImportError:
    from config import get_monitor_path

logger = logging.getLogger('gpuiservice')


class DirectoryMonitor:
    """Monitor directory for ADMX file changes and reload data"""

    def __init__(
        self,
        data_store: Any,
        reload_callback: Optional[Callable[[], None]] = None
    ) -> None:
        self.data_store = data_store
        self.reload_callback = reload_callback
        self.monitor: Optional[Gio.FileMonitor] = None
        self.monitored_path: Optional[str] = None

    def on_file_changed(
        self,
        monitor: Gio.FileMonitor,
        file: Gio.File,
        other_file: Optional[Gio.File],
        event_type: Gio.FileMonitorEvent
    ) -> None:
        """Callback when ADMX files change in monitored directory"""
        if event_type in (Gio.FileMonitorEvent.CHANGED,
                         Gio.FileMonitorEvent.CREATED,
                         Gio.FileMonitorEvent.DELETED,
                         Gio.FileMonitorEvent.MOVED):
            logger.info(f"Directory change detected: {file.get_path()} ({event_type.value_name})")

            # Reload ADMX data from directory
            self.reload_data()

    def reload_data(self) -> None:
        """Reload ADMX data from monitored directory"""
        if self.monitored_path:
            logger.info(f"Reloading ADMX data from {self.monitored_path}")
            self.data_store.load_from_directory(self.monitored_path)

            # Call custom reload callback if provided
            if self.reload_callback:
                try:
                    self.reload_callback()
                except Exception as e:
                    logger.exception(f"Error in reload callback: {e}")

    def start_monitoring(self) -> None:
        """Start monitoring the directory"""
        self.monitored_path = get_monitor_path()

        # Create directory if it doesn't exist
        path_obj = Path(self.monitored_path)
        try:
            path_obj.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            logger.error(f"Permission denied creating directory {self.monitored_path}: {e}")
        except OSError as e:
            logger.error(f"Could not create directory {self.monitored_path}: {e}")

        # Initial load
        self.reload_data()

        # Setup file monitor
        try:
            file = Gio.File.new_for_path(self.monitored_path)
            self.monitor = file.monitor_directory(Gio.FileMonitorFlags.NONE, None)
            self.monitor.connect('changed', self.on_file_changed)
            logger.info(f"Started monitoring directory: {self.monitored_path}")
        except (OSError, GLib.Error) as e:
            logger.error(f"Failed to setup directory monitor: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error setting up directory monitor: {e}")

    def stop_monitoring(self) -> None:
        """Stop monitoring"""
        if self.monitor:
            self.monitor.cancel()
            self.monitor = None
            logger.info("Stopped directory monitoring")