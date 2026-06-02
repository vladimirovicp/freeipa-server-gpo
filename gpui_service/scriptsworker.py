import logging
import os
import re
import tempfile
from pathlib import Path

try:
    from . import utils
    from .config import DEFAULT_SYSVOL_PATH
except ImportError:
    import utils
    from config import DEFAULT_SYSVOL_PATH

logger = logging.getLogger('gpuiservice')

SCRIPTS_CONFIG = {
    ('Machine', 'scripts'):   {'sections': ['Startup', 'Shutdown'], 'file': 'scripts.ini'},
    ('Machine', 'psscripts'): {'sections': ['Startup', 'Shutdown'], 'file': 'psscripts.ini'},
    ('User', 'scripts'):      {'sections': ['Logon', 'Logoff'],     'file': 'scripts.ini'},
    ('User', 'psscripts'):    {'sections': ['Logon', 'Logoff'],     'file': 'psscripts.ini'},
}


class ScriptsWorker:
    """Read/write Group Policy scripts (scripts.ini / psscripts.ini)."""

    def __init__(self, sysvol_path=DEFAULT_SYSVOL_PATH):
        self.sysvol_path = sysvol_path

    def read_scripts(self, gpo_path, scope, script_type):
        """
        Read scripts.ini or psscripts.ini for a GPO.

        Args:
            gpo_path: Resolved path to GPO within sysvol
            scope: 'Machine' or 'User'
            script_type: 'scripts' or 'psscripts'

        Returns:
            dict {section_name: [{"cmdLine": ..., "parameters": ...}, ...]}
        """
        config = SCRIPTS_CONFIG.get((scope, script_type))
        if not config:
            logger.error(f"Unknown scripts config for scope={scope}, type={script_type}")
            return {}

        ini_path = self._get_ini_path(gpo_path, scope, config['file'])
        result = {s: [] for s in config['sections']}

        if not os.path.exists(ini_path):
            logger.debug(f"Scripts file not found: {ini_path}")
            return result

        try:
            content = self._read_utf16le(ini_path)
            parsed = self._parse_ini(content)

            for section_name in config['sections']:
                if section_name in parsed:
                    result[section_name] = self._parse_section(parsed[section_name])

            return result
        except Exception as e:
            logger.error(f"Error reading scripts from {ini_path}: {e}")
            return result

    def write_scripts(self, gpo_path, scope, script_type, scripts_data):
        """
        Write scripts.ini or psscripts.ini for a GPO.

        Args:
            gpo_path: Resolved path to GPO within sysvol
            scope: 'Machine' or 'User'
            script_type: 'scripts' or 'psscripts'
            scripts_data: dict {section_name: [{"cmdLine": ..., "parameters": ...}, ...]}

        Returns:
            True if successful
        """
        config = SCRIPTS_CONFIG.get((scope, script_type))
        if not config:
            logger.error(f"Unknown scripts config for scope={scope}, type={script_type}")
            return False

        ini_path = self._get_ini_path(gpo_path, scope, config['file'])

        scripts_dir = os.path.dirname(ini_path)
        os.makedirs(scripts_dir, exist_ok=True)

        for section_name in config['sections']:
            section_dir = os.path.join(scripts_dir, section_name)
            os.makedirs(section_dir, exist_ok=True)

        lines = []
        for section_name in config['sections']:
            entries = scripts_data.get(section_name, [])
            lines.append(f"[{section_name}]\n")
            for i, entry in enumerate(entries):
                cmd = entry.get('cmdLine', '')
                params = entry.get('parameters', '')
                lines.append(f"{i}CmdLine={cmd}\n")
                lines.append(f"{i}Parameters={params}\n")

        content = ''.join(lines)

        try:
            self._write_utf16le(ini_path, content)
            logger.info(f"Scripts written to {ini_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing scripts to {ini_path}: {e}")
            return False

    def _get_ini_path(self, gpo_path, scope, filename):
        return os.path.join(gpo_path, scope, 'Scripts', filename)

    @staticmethod
    def _read_utf16le(path):
        with open(path, 'rb') as f:
            raw = f.read()
        if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
            return raw.decode('utf-16')
        try:
            return raw.decode('utf-16-le')
        except UnicodeDecodeError:
            return raw.decode('utf-8', errors='replace')

    @staticmethod
    def _write_utf16le(path, content):
        fd, tmp_path = tempfile.mkstemp(suffix='.ini', dir=os.path.dirname(path))
        try:
            with os.fdopen(fd, 'w', encoding='utf-16-le') as f:
                f.write('\ufeff')
                f.write(content)
            os.replace(tmp_path, path)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    @staticmethod
    def _parse_ini(content):
        sections = {}
        current_section = None
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip()
                if current_section not in sections:
                    sections[current_section] = {}
                continue
            if current_section is not None and '=' in line:
                key, _, value = line.partition('=')
                sections[current_section][key.strip()] = value.strip()
        return sections

    @staticmethod
    def _parse_section(section_dict):
        entries = []
        cmd_line_re = re.compile(r'^(\d+)CmdLine$')
        params_re = re.compile(r'^(\d+)Parameters$')

        cmd_lines = {}
        params = {}

        for key, value in section_dict.items():
            m = cmd_line_re.match(key)
            if m:
                cmd_lines[int(m.group(1))] = value
                continue
            m = params_re.match(key)
            if m:
                params[int(m.group(1))] = value

        all_indices = sorted(set(cmd_lines.keys()) | set(params.keys()))

        for idx in all_indices:
            entries.append({
                'cmdLine': cmd_lines.get(idx, ''),
                'parameters': params.get(idx, ''),
            })

        return entries
