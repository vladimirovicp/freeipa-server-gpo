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
ServiceDaemon - Main daemon class managing DBus service and GLib main loop
"""

import sys
import signal
import threading
import traceback
from typing import Any, Optional

from gi.repository import GLib, Gio
import dbus
import dbus.mainloop.glib
import logging

try:
    from .datastore import GPODataStore
    from .monitor import DirectoryMonitor
    from .service import GPUIService
    from .config import get_monitor_path, get_sysvol_path
except ImportError:
    from datastore import GPODataStore
    from monitor import DirectoryMonitor
    from service import GPUIService
    from config import get_monitor_path, get_sysvol_path

logger = logging.getLogger('gpuiservice')


class ServiceDaemon:
    """Main daemon class managing DBus service and GLib main loop"""

    def __init__(self, daemon_mode: bool = True) -> None:
        self.daemon_mode: bool = daemon_mode
        self.loop: Optional[GLib.MainLoop] = None
        self.bus: Optional[dbus.SystemBus] = None
        self.service: Optional[GPUIService] = None
        self.data_store: Optional[GPODataStore] = None
        self.monitor: Optional[DirectoryMonitor] = None
        self.shutdown_event: threading.Event = threading.Event()

    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum: int, frame: Any) -> None:
        """Handle termination signals"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown_event.set()

    def setup_dbus(self) -> bool:
        """Setup DBus connection and register service"""
        try:
            logger.debug("Setting DBus main loop...")
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            logger.debug("Connecting to system bus...")
            self.bus = dbus.SystemBus()
            logger.debug(f"System bus connected: {self.bus}")

            # Request bus name
            logger.debug("Requesting bus name 'org.altlinux.gpuiservice'...")
            bus_name = dbus.service.BusName('org.altlinux.gpuiservice', self.bus)
            logger.debug(f"Bus name acquired: {bus_name}")

            # Create data store
            sysvol_path = get_sysvol_path()
            monitor_path = get_monitor_path()
            self.data_store = GPODataStore(sysvol_path)
            self.data_store.load_from_directory(monitor_path)

            logger.debug(f"self.data_store_dict {type(self.data_store)}")

            # Create service object
            logger.debug("Creating GPUIService object...")
            self.service = GPUIService(bus_name, '/org/altlinux/gpuiservice', self.data_store)

            logger.info("DBus service registered successfully")
            return True
        except dbus.exceptions.DBusException as e:
            logger.error(f"DBus error during setup: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error setting up DBus: {e}")
            return False

    def setup_monitor(self) -> bool:
        """Setup directory monitoring"""
        try:
            def on_reload() -> None:
                logger.info("Data reloaded from monitored directory")

            self.monitor = DirectoryMonitor(self.data_store, reload_callback=on_reload)
            self.monitor.start_monitoring()
            logger.info("Directory monitoring started")
            return True
        except OSError as e:
            logger.error(f"I/O error setting up directory monitor: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error setting up directory monitor: {e}")
            return False

    def run(self) -> int:
        """Main daemon run method"""
        logger.debug("ServiceDaemon.run() called")
        logger.info("Starting GPUIService daemon")

        # Setup signal handlers
        self.setup_signal_handlers()
        logger.debug("Signal handlers setup")

        # Setup DBus
        logger.debug("Setting up DBus...")
        if not self.setup_dbus():
            logger.error("Failed to setup DBus, exiting")
            return 1
        logger.debug("DBus setup successful")

        # Setup directory monitoring
        logger.debug("Setting up directory monitor...")
        if not self.setup_monitor():
            logger.debug("Directory monitoring setup failed, continuing without it")
        logger.debug("Directory monitor setup complete")

        # Create and run GLib main loop
        self.loop = GLib.MainLoop()

        # Run in background thread if in daemon mode
        if self.daemon_mode:
            loop_thread = threading.Thread(target=self.loop.run)
            loop_thread.daemon = True
            loop_thread.start()

            logger.info("Daemon running in background mode")

            # Wait for shutdown signal
            self.shutdown_event.wait()

            # Stop monitoring
            if self.monitor:
                self.monitor.stop_monitoring()

            # Quit the loop
            self.loop.quit()
            loop_thread.join(timeout=5)
        else:
            # Run in foreground
            logger.info("Running in foreground mode")
            try:
                self.loop.run()
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
            finally:
                if self.monitor:
                    self.monitor.stop_monitoring()
                self.loop.quit()

        logger.info("GPUIService daemon stopped")
        return 0
