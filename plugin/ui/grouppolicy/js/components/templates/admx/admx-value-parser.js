define(['./admx-constants', './admx-policy-normalizers'], function(__dep0, __dep1) {
var { ADMX_DEFAULT_STATE, ADMX_DISABLED_VALUE_MARKER } = __dep0;
var { isPlainObject, normalizeAdmxState } = __dep1;

function unwrapCurrentValue(rawValue) {
    if (Array.isArray(rawValue)) {
        return rawValue.length > 0
            ? unwrapCurrentValue(rawValue[0])
            : null;
    }

    if (isPlainObject(rawValue)) {
        const candidateKeys = ['result', 'value', 'currentValue'];

        for (const key of candidateKeys) {
            if (Object.prototype.hasOwnProperty.call(rawValue, key)) {
                return unwrapCurrentValue(rawValue[key]);
            }
        }
    }

    return rawValue;
}

function parseStringValueAsAdmxState(stringValue) {
    if (stringValue === null || stringValue === undefined || stringValue === '') {
        return {
            hasData: false,
            state: ADMX_DEFAULT_STATE,
            value: null,
        };
    }

    const str = String(stringValue);

    if (str === ADMX_DISABLED_VALUE_MARKER) {
        return {
            hasData: true,
            state: 'disabled',
            value: null,
        };
    }

    const delimiterIndex = str.indexOf(';');

    if (delimiterIndex === -1) {
        return {
            hasData: true,
            state: 'enabled',
            value: str,
        };
    }

    return {
        hasData: true,
        state: normalizeAdmxState(str.slice(0, delimiterIndex)),
        value: str.slice(delimiterIndex + 1),
    };
}

function parseAdmxCurrentValue(rawValue) {
    const normalizedRawValue = unwrapCurrentValue(rawValue);

    if (isPlainObject(normalizedRawValue)) {
        if (Object.keys(normalizedRawValue).length === 0) {
            return {
                hasData: false,
                state: ADMX_DEFAULT_STATE,
                value: null,
            };
        }

        if (Object.prototype.hasOwnProperty.call(normalizedRawValue, 'value_data')) {
            return parseStringValueAsAdmxState(normalizedRawValue.value_data);
        }

        if (Object.prototype.hasOwnProperty.call(normalizedRawValue, 'state')) {
            return {
                hasData: true,
                state: normalizeAdmxState(normalizedRawValue.state),
                value: Object.prototype.hasOwnProperty.call(normalizedRawValue, 'value')
                    ? normalizedRawValue.value
                    : '',
            };
        }
    }

    if (normalizedRawValue === null || normalizedRawValue === undefined || normalizedRawValue === '') {
        return {
            hasData: false,
            state: ADMX_DEFAULT_STATE,
            value: null,
        };
    }

    return parseStringValueAsAdmxState(normalizedRawValue);
}

function buildAdmxSetValue(state, fieldValue) {
    const normalizedState = normalizeAdmxState(state);
    const normalizedValue = fieldValue === null || fieldValue === undefined
        ? ''
        : String(fieldValue);

    if (normalizedState === 'disabled') {
        return ADMX_DISABLED_VALUE_MARKER;
    }

    if (normalizedState === 'enabled') {
        return normalizedValue;
    }

    return '';
}

    return {
        unwrapCurrentValue,
        parseStringValueAsAdmxState,
        parseAdmxCurrentValue,
        buildAdmxSetValue,
    };
});
