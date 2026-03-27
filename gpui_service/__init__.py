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
gpuiservice - API service for webGPUI to manage GPT directory contents
"""

try:
    from .config import get_monitor_path, get_sysvol_path, get_gsettings
    from .datastore import GPODataStore
    from .monitor import DirectoryMonitor
    from .service import GPUIService
    from .daemon import ServiceDaemon
    from .gptworker import GPTWorker
    from .gpprefs import GPPrefsWorker
    from .utils import resolve_gpo_path, normalize_path_separators, is_unc_path
except ImportError:
    from config import get_monitor_path, get_sysvol_path, get_gsettings
    from datastore import GPODataStore
    from monitor import DirectoryMonitor
    from service import GPUIService
    from daemon import ServiceDaemon
    from gptworker import GPTWorker
    from gpprefs import GPPrefsWorker
    from utils import resolve_gpo_path, normalize_path_separators, is_unc_path

__all__ = [
    'get_monitor_path',
    'get_sysvol_path',
    'get_gsettings',
    'GPODataStore',
    'DirectoryMonitor',
    'GPUIService',
    'ServiceDaemon',
    'GPTWorker',
    'GPPrefsWorker',
    'resolve_gpo_path',
    'normalize_path_separators',
    'is_unc_path',
]