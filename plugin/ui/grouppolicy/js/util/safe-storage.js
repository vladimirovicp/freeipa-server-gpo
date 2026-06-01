define([], function() {
/**
 * Safe localStorage adapter.
 *
 * Wraps all localStorage operations in try/catch to prevent UI crashes
 * from corrupted JSON, SecurityError, QuotaExceededError, or disabled storage.
 *
 * Schema validation uses predicate functions: (data) => boolean.
 * If data fails validation, fallback is returned — no silent coercion.
 *
 * @module safe-storage
 */

/**
 * Safely reads and parses JSON from localStorage.
 * Returns fallback if: key is missing, JSON is corrupt, or schema validation fails.
 *
 * @param {string} key - localStorage key
 * @param {((data: unknown) => boolean)|null} schema - validation predicate, null to skip
 * @param {*} fallback - value returned on any failure
 * @returns {*} parsed value or fallback
 */
function getItemSafe(key, schema, fallback) {
    try {
        const raw = localStorage.getItem(key);
        if (raw === null) return fallback;

        const parsed = JSON.parse(raw);

        if (typeof schema === 'function' && !schema(parsed)) {
            /*
             * MIGRATION POINT: data exists but doesn't match the current schema.
             * Future data-migration logic can be inserted here (e.g. version-aware
             * transforms) before falling back. For now — return fallback as-is.
             */
            console.warn(
                `[safe-storage] "${key}": data failed schema validation, using fallback`
            );
            return fallback;
        }

        return parsed;
    } catch (error) {
        console.warn(
            `[safe-storage] "${key}": read/parse error, using fallback`,
            error
        );
        return fallback;
    }
}

/**
 * Safely serializes and writes a value to localStorage.
 * Optionally validates the value against a schema before writing.
 *
 * @param {string} key - localStorage key
 * @param {*} value - value to serialize
 * @param {((data: unknown) => boolean)|null} [schema=null] - validation predicate
 * @returns {boolean} true if write succeeded
 */
function setItemSafe(key, value, schema = null) {
    try {
        if (typeof schema === 'function' && !schema(value)) {
            console.warn(
                `[safe-storage] "${key}": value failed schema validation, write rejected`
            );
            return false;
        }
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (error) {
        console.warn(`[safe-storage] "${key}": write error`, error);
        return false;
    }
}

/**
 * Safely removes a key from localStorage.
 *
 * @param {string} key - localStorage key
 * @returns {boolean} true if removal succeeded
 */
function removeItemSafe(key) {
    try {
        localStorage.removeItem(key);
        return true;
    } catch (error) {
        console.warn(`[safe-storage] "${key}": remove error`, error);
        return false;
    }
}

/**
 * Ensures a localStorage key is initialized with seed data.
 * Writes seed only if: key is absent, JSON is corrupt, or data fails schema.
 *
 * Call this explicitly at app startup — never as an import side effect.
 *
 * @param {string} key - localStorage key
 * @param {*} seed - default data to write when key is missing or invalid
 * @param {((data: unknown) => boolean)|null} [schema=null] - validation predicate
 * @returns {boolean} true if seed was written (data was missing or invalid)
 */
function ensureInitialized(key, seed, schema = null) {
    const existing = getItemSafe(key, schema, undefined);
    if (existing !== undefined) return false;

    return setItemSafe(key, seed, schema);
}
    return { getItemSafe, setItemSafe, removeItemSafe, ensureInitialized };
});
