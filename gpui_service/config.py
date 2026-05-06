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
Shared configuration for GPUIService - GSettings access.

This module provides centralized access to GSettings configuration,
eliminating code duplication between daemon.py and monitor.py.
"""

import logging
from typing import Optional

from gi.repository import Gio

logger = logging.getLogger('gpuiservice')

DEFAULT_MONITOR_PATH = '/usr/share/PolicyDefinitions'
DEFAULT_SYSVOL_PATH = '/var/lib/freeipa/sysvol'
GSETTINGS_SCHEMA = 'org.altlinux.gpuiservice'
SUPPORTED_LOCALES = {'ru-RU', 'en-US'}


def get_gsettings() -> Optional[Gio.Settings]:
    """
    Get GSettings object for gpuiservice schema.

    Returns:
        Gio.Settings object if available, None otherwise.
    """
    try:
        return Gio.Settings.new(GSETTINGS_SCHEMA)
    except Exception as e:
        logger.debug(f"Could not load GSettings schema '{GSETTINGS_SCHEMA}': {e}")
        return None


def get_monitor_path(settings: Optional[Gio.Settings] = None) -> str:
    """
    Get ADMX policy definitions monitor path from GSettings or default.

    Args:
        settings: Optional Gio.Settings object. If None, will attempt
                  to get GSettings automatically.

    Returns:
        Path to monitor directory for ADMX files.
    """
    if settings is None:
        settings = get_gsettings()

    if settings:
        try:
            path = settings.get_string('monitor-path')
            if path:
                logger.info(f"Using monitor path from GSettings: {path}")
                return path
        except Exception as e:
            logger.debug(f"Could not read 'monitor-path' from GSettings: {e}")

    logger.info(f"Using default monitor path: {DEFAULT_MONITOR_PATH}")
    return DEFAULT_MONITOR_PATH


def get_sysvol_path(settings: Optional[Gio.Settings] = None) -> str:
    """
    Get FreeIPA sysvol path from GSettings or default.

    Args:
        settings: Optional Gio.Settings object. If None, will attempt
                  to get GSettings automatically.

    Returns:
        Path to FreeIPA sysvol directory.
    """
    if settings is None:
        settings = get_gsettings()

    if settings:
        try:
            path = settings.get_string('sysvol-path')
            if path:
                logger.info(f"Using sysvol path from GSettings: {path}")
                return path
        except Exception as e:
            logger.debug(f"Could not read 'sysvol-path' from GSettings: {e}")

    logger.info(f"Using default sysvol path: {DEFAULT_SYSVOL_PATH}")
    return DEFAULT_SYSVOL_PATH


def get_locale(settings: Optional[Gio.Settings] = None) -> str:
    """
    Get locale from GSettings for ADMX parsing.

    Args:
        settings: Optional Gio.Settings object. If None, will attempt
                  to get GSettings automatically.

    Returns:
        Locale string from GSettings, or empty string (use system locale).
    """
    if settings is None:
        settings = get_gsettings()

    if settings:
        try:
            locale = settings.get_string('locale')
            if locale:
                logger.info(f"Using locale from GSettings: {locale}")
                return locale
        except Exception as e:
            logger.debug(f"Could not read 'locale' from GSettings: {e}")

    logger.info("Using system locale (GSettings locale is empty)")
    return ''


def set_locale(locale: str, settings: Optional[Gio.Settings] = None) -> bool:
    """
    Set locale in GSettings for ADMX parsing.

    Args:
        locale: Locale string to set (e.g., 'ru-RU', 'en-US')
        settings: Optional Gio.Settings object. If None, will attempt
                  to get GSettings automatically.

    Returns:
        True if successful, False otherwise.
    """
    if settings is None:
        settings = get_gsettings()

    if settings:
        try:
            settings.set_string('locale', locale)
            logger.info(f"Set locale in GSettings: {locale}")
            return True
        except Exception as e:
            logger.error(f"Could not set 'locale' in GSettings: {e}")

    return False
