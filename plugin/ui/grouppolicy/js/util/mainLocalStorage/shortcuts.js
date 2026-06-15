define(['../safe-storage'], function(__dep0) {
var {
    getItemSafe,
    setItemSafe,
    removeItemSafe,
    ensureInitialized,
} = __dep0;

/**
 * Shortcuts localStorage module.
 *
 * Provides safe read/write/init for the 'shortcuts' key in localStorage.
 * All operations go through the safe-storage adapter — no raw JSON.parse
 * or direct localStorage calls — to prevent UI crashes on corrupted data.
 *
 * IMPORTANT: This module does NOT auto-initialize on import.
 * Call {@link initShortcutsStorage} explicitly at app startup.
 */


const STORAGE_KEY = 'shortcuts';

/** Valid TARGET_TYPE values matching the UI form select: 0 (filesystem), 1 (URL), 2 (shell) */
const VALID_TARGET_TYPES = new Set([0, 1, 2]);

/** Default seed data — structure matches Shortcuts.md field spec */
const SHORTCUTS_SEED = [
    {
        basic: {
            "ACTION": 3,
            "SHORTCUT_PATH": "Mail",
            "TARGET_TYPE": 2,
            "TARGET_PATH": "/usr/bin/thunderbird",
            "LOCATION": 1,
            "ARGUMENTS": "",
            "START_IN": "",
            "SHORTCUT_KEY": "",
            "WINDOW": 0,
            "COMMENT": "Комментарий для Mail",
            "ICON_PATH": "/usr/share/icons/default/application.png",
            "ICON_INDEX": ""
        },
        common: {
            "stopOnErrorCheckBox": true,
            "userContextCheckBox": false,
            "removeThisCheckBox": false,
            "description": "моё краткое описание"
        }
    },
    {
        basic: {
            "ACTION": 0,
            "SHORTCUT_PATH": "Mail",
            "TARGET_TYPE": 2,
            "TARGET_PATH": "/usr/bin/thunderbird",
            "LOCATION": 2,
            "ARGUMENTS": "",
            "START_IN": "",
            "SHORTCUT_KEY": "",
            "WINDOW": 0,
            "COMMENT": "",
            "ICON_PATH": "/usr/share/icons/default/application.png",
            "ICON_INDEX": ""
        },
        common: {
            "stopOnErrorCheckBox": false,
            "userContextCheckBox": true,
            "removeThisCheckBox": false,
            "description": "моё краткое описание N2"
        }
    },
    {
        basic: {
            "ACTION": 2,
            "SHORTCUT_PATH": "Mail",
            "TARGET_TYPE": 2,
            "TARGET_PATH": "/usr/bin/thunderbird",
            "LOCATION": 9,
            "ARGUMENTS": "",
            "START_IN": "",
            "SHORTCUT_KEY": "",
            "WINDOW": 0,
            "COMMENT": "",
            "ICON_PATH": "/usr/share/icons/default/application.png",
            "ICON_INDEX": ""
        },
        common: {
            "stopOnErrorCheckBox": false,
            "userContextCheckBox": false,
            "removeThisCheckBox": true,
            "description": "моё краткое описание 3"
        }
    }
];

/**
 * Validates a single shortcut entry structure.
 *
 * Required fields and types:
 *   basic.ACTION          — number  (0–3: create/replace/update/delete)
 *   basic.SHORTCUT_PATH   — string
 *   basic.TARGET_TYPE      — number, must be in VALID_TARGET_TYPES {0, 1, 2}
 *   basic.TARGET_PATH      — string
 *   common.stopOnErrorCheckBox  — boolean
 *   common.userContextCheckBox  — boolean
 *   common.removeThisCheckBox   — boolean
 *
 * MIGRATION POINT: if legacy data contains TARGET_TYPE values outside {0,1,2},
 * it will fail this validation. Add version-aware migration before this check
 * if backward-compatible loading of old data is needed.
 *
 * @param {unknown} item
 * @returns {boolean}
 */
function isValidShortcutEntry(item) {
    if (!item || typeof item !== 'object') return false;

    const { basic, common } = /** @type {Record<string, any>} */ (item);
    if (!basic || typeof basic !== 'object') return false;
    if (!common || typeof common !== 'object') return false;

    if (typeof basic.ACTION !== 'number') return false;
    if (typeof basic.SHORTCUT_PATH !== 'string') return false;
    if (typeof basic.TARGET_TYPE !== 'number' || !VALID_TARGET_TYPES.has(basic.TARGET_TYPE)) return false;
    if (typeof basic.TARGET_PATH !== 'string') return false;

    if (typeof common.stopOnErrorCheckBox !== 'boolean') return false;
    if (typeof common.userContextCheckBox !== 'boolean') return false;
    if (typeof common.removeThisCheckBox !== 'boolean') return false;

    return true;
}

/**
 * Schema predicate for the shortcuts array.
 * Accepts an empty array (no shortcuts yet) or an array where every entry is valid.
 *
 * MIGRATION POINT: if the schema evolves (e.g. new required fields),
 * add version-aware transform logic here or in {@link ensureInitialized}
 * before this check runs.
 *
 * @param {unknown} data
 * @returns {boolean}
 */
function validateShortcutsSchema(data) {
    if (!Array.isArray(data)) return false;
    return data.every(isValidShortcutEntry);
}

/**
 * Explicitly initializes shortcuts in localStorage.
 * Seeds default data only if key is missing, JSON is corrupt, or schema is invalid.
 *
 * Must be called once at app startup — NOT triggered by import.
 */
function initShortcutsStorage() {
    const seeded = ensureInitialized(
        STORAGE_KEY,
        SHORTCUTS_SEED,
        validateShortcutsSchema
    );
    if (seeded) {
        console.log('Shortcuts localStorage initialized with seed data');
    } else {
        console.log('Shortcuts localStorage already contains valid data');
    }
}

/**
 * Reads shortcuts from localStorage with schema validation.
 * Returns [] if data is missing, corrupt, or fails schema validation.
 *
 * Why fallback is []: every consumer iterates the result with .map/.forEach,
 * so an empty array is the safest default that won't break the UI.
 *
 * @returns {Array<Object>} array of shortcut entries
 */
function getShortcutsFromLocalStorage() {
    return getItemSafe(STORAGE_KEY, validateShortcutsSchema, []);
}

/**
 * Saves shortcuts array to localStorage with schema validation.
 *
 * @param {Array<Object>} shortcuts
 * @returns {boolean} true if write succeeded
 */
function saveShortcutsToLocalStorage(shortcuts) {
    return setItemSafe(STORAGE_KEY, shortcuts, validateShortcutsSchema);
}

/**
 * Removes shortcuts from localStorage and re-seeds with defaults.
 */
function resetShortcutsLocalStorage() {
    removeItemSafe(STORAGE_KEY);
    initShortcutsStorage();
}
    return { validateShortcutsSchema, initShortcutsStorage, getShortcutsFromLocalStorage, saveShortcutsToLocalStorage, resetShortcutsLocalStorage, VALID_TARGET_TYPES };
});
