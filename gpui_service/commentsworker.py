import logging
import os
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from . import utils
    from .config import DEFAULT_SYSVOL_PATH
except ImportError:
    import utils
    from config import DEFAULT_SYSVOL_PATH

logger = logging.getLogger('gpuiservice')

CMTX_NS = "http://www.microsoft.com/GroupPolicy/CommentDefinitions"
CMTX_NS_MAP = {
    "xsd": "http://www.w3.org/2001/XMLSchema",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "cmtx": CMTX_NS,
}


class CommentsWorker:
    """Read/write Group Policy comments (CMTX/CMTL)."""

    def __init__(self, sysvol_path=DEFAULT_SYSVOL_PATH):
        self.sysvol_path = sysvol_path

    def read_comments(self, gpo_path, scope, locale=''):
        cmtx_path = self._get_cmtx_path(gpo_path, scope)
        utils.validate_path_in_sysvol(cmtx_path, self.sysvol_path)
        if not os.path.exists(cmtx_path):
            logger.debug(f"CMTX file not found: {cmtx_path}")
            return {}

        try:
            tree = ET.parse(cmtx_path)
            root = tree.getroot()
        except ET.ParseError as e:
            logger.error(f"Error parsing CMTX {cmtx_path}: {e}")
            return {}

        namespaces = self._parse_namespaces(root)
        string_table = self._load_string_table(root)

        if locale:
            cmtl_table = self._load_cmtl(gpo_path, scope, locale)
            if cmtl_table:
                string_table.update(cmtl_table)

        comments = {}
        for comment_el in root.iter(f"{{{CMTX_NS}}}comment"):
            policy_ref = comment_el.get('policyRef', '')
            comment_text_ref = comment_el.get('commentText', '')

            policy_name = self._extract_policy_name(policy_ref)
            resource_key = self._resolve_resource_ref(comment_text_ref)
            actual_text = string_table.get(resource_key, comment_text_ref)

            if policy_name:
                comments[policy_name] = actual_text

        return comments

    def save_comment(self, gpo_path, scope, policy_ref, comment_text, namespace=''):
        """
        Add or update a single comment in comment.cmtx.

        Args:
            gpo_path: Resolved path to GPO within sysvol
            scope: 'Machine' or 'User'
            policy_ref: Policy identifier (e.g., 'Namespace.PolicyName')
            comment_text: Comment text to save
            namespace: ADMX target namespace (optional)

        Returns:
            True if successful
        """
        cmtx_path = self._get_cmtx_path(gpo_path, scope)
        utils.validate_path_in_sysvol(cmtx_path, self.sysvol_path)
        comments = self.read_comments(gpo_path, scope)

        parts = policy_ref.split(':', 1)
        if len(parts) == 2:
            policy_name = parts[1]
            ns = parts[0] if '.' not in parts[0] else namespace
        else:
            policy_name = policy_ref
            ns = namespace or 'unknown'

        comments[policy_name] = comment_text

        return self._write_cmtx(cmtx_path, comments, ns)

    def delete_comment(self, gpo_path, scope, policy_ref):
        """
        Delete a single comment by policy reference.

        Args:
            gpo_path: Resolved path to GPO within sysvol
            scope: 'Machine' or 'User'
            policy_ref: Policy name or 'ns:PolicyName'

        Returns:
            True if successful
        """
        cmtx_path = self._get_cmtx_path(gpo_path, scope)
        utils.validate_path_in_sysvol(cmtx_path, self.sysvol_path)
        comments = self.read_comments(gpo_path, scope)

        parts = policy_ref.split(':', 1)
        policy_name = parts[1] if len(parts) == 2 else policy_ref

        if policy_name not in comments:
            logger.debug(f"Comment not found for policy: {policy_name}")
            return True

        del comments[policy_name]

        if not comments:
            if os.path.exists(cmtx_path):
                os.remove(cmtx_path)
            return True

        return self._write_cmtx(cmtx_path, comments, '')

    @staticmethod
    def _get_cmtx_path(gpo_path, scope):
        return os.path.join(gpo_path, scope, 'comment.cmtx')

    @staticmethod
    def _get_cmtl_path(gpo_path, scope, locale):
        return os.path.join(gpo_path, scope, locale, 'comment.cmtl')

    @staticmethod
    def _parse_namespaces(root):
        ns_map = {}
        for using_el in root.iter(f"{{{CMTX_NS}}}using"):
            prefix = using_el.get('prefix', '')
            namespace = using_el.get('namespace', '')
            if prefix and namespace:
                ns_map[prefix] = namespace
        return ns_map

    @staticmethod
    def _load_string_table(root):
        table = {}
        for string_el in root.iter(f"{{{CMTX_NS}}}string"):
            sid = string_el.get('id', '')
            text = (string_el.text or '').strip()
            if sid:
                table[sid] = text
        return table

    def _load_cmtl(self, gpo_path, scope, locale):
        cmtl_path = self._get_cmtl_path(gpo_path, scope, locale)
        if not os.path.exists(cmtl_path):
            return {}

        try:
            tree = ET.parse(cmtl_path)
            root = tree.getroot()
        except ET.ParseError as e:
            logger.debug(f"Error parsing CMTL {cmtl_path}: {e}")
            return {}

        return self._load_string_table(root)

    @staticmethod
    def _extract_policy_name(policy_ref):
        if ':' in policy_ref:
            parts = policy_ref.split(':', 1)
            if parts[0].startswith('ns') and len(parts[0]) <= 4:
                return parts[1]
        return policy_ref

    @staticmethod
    def _resolve_resource_ref(ref):
        if ref.startswith('$(resource.') and ref.endswith(')'):
            return ref[11:-1]
        return ref

    def _write_cmtx(self, cmtx_path, comments, default_namespace):
        ns_set = set()
        if default_namespace:
            ns_set.add(default_namespace)

        dir_path = os.path.dirname(cmtx_path)
        os.makedirs(dir_path, exist_ok=True)

        ns_list = sorted(ns_set) if ns_set else ['unknown']
        ns_prefixes = {ns: f"ns{i}" for i, ns in enumerate(ns_list)}

        attribs = {
            'revision': '1.0',
            'schemaVersion': '1.0',
        }

        root = ET.Element(f"{{{CMTX_NS}}}policyComments", attribs)
        for prefix, uri in [('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema'),
                            ('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')]:
            root.set(prefix, uri)

        ns_element = ET.SubElement(root, f"{{{CMTX_NS}}}policyNamespaces")
        for ns, prefix in ns_prefixes.items():
            using = ET.SubElement(ns_element, f"{{{CMTX_NS}}}using")
            using.set('prefix', prefix)
            using.set('namespace', ns)

        comments_el = ET.SubElement(root, f"{{{CMTX_NS}}}comments")
        adm_template = ET.SubElement(comments_el, f"{{{CMTX_NS}}}admTemplate")

        resources = ET.SubElement(root, f"{{{CMTX_NS}}}resources")
        resources.set('minRequiredRevision', '1.0')
        string_table_el = ET.SubElement(resources, f"{{{CMTX_NS}}}stringTable")

        for i, (policy_name, text) in enumerate(comments.items()):
            prefix = ns_prefixes.get(ns_list[0], 'ns0') if ns_list else f"ns{i}"
            resource_key = f"{prefix}_{policy_name}"

            comment_el = ET.SubElement(adm_template, f"{{{CMTX_NS}}}comment")
            comment_el.set('policyRef', f"{prefix}:{policy_name}")
            comment_el.set('commentText', f"$(resource.{resource_key})")

            string_el = ET.SubElement(string_table_el, f"{{{CMTX_NS}}}string")
            string_el.set('id', resource_key)
            string_el.text = text

        try:
            self._atomic_write_xml(cmtx_path, root)
            logger.info(f"Comments written to {cmtx_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing CMTX to {cmtx_path}: {e}")
            return False

    @staticmethod
    def _atomic_write_xml(path, root_element):
        fd, tmp_path = tempfile.mkstemp(
            suffix='.cmtx', dir=os.path.dirname(path)
        )
        try:
            tree = ET.ElementTree(root_element)
            with os.fdopen(fd, 'wb') as f:
                tree.write(f, encoding='utf-8', xml_declaration=True)
            os.replace(tmp_path, path)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise
