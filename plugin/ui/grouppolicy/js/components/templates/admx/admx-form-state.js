define(['./admx-constants', './admx-policy-normalizers'], function(__dep0, __dep1) {
var { ADMX_DEFAULT_STATE } = __dep0;
var { getDefaultControlValue } = __dep1;

function setControlsDisabledState(rootElement, shouldDisable) {
    if (!rootElement) {
        return;
    }

    const controls = rootElement.querySelectorAll('.gp__admx-options input, .gp__admx-options select, .gp__admx-options textarea, .gp__admx-options button.packages-control__btn-edit');

    controls.forEach((control) => {
        control.disabled = shouldDisable;
    });
}

function getSelectedAdmxState(rootElement) {
    return rootElement?.querySelector('input[name="admx-state"]:checked')?.value ?? ADMX_DEFAULT_STATE;
}

function setSelectedAdmxState(rootElement, state = ADMX_DEFAULT_STATE) {
    if (!rootElement) {
        return;
    }

    const normalizedState = typeof state === 'string' && state.length > 0
        ? state
        : ADMX_DEFAULT_STATE;

    const radioToSelect = rootElement.querySelector(`input[name="admx-state"][value="${CSS.escape(normalizedState)}"]`);

    if (radioToSelect instanceof HTMLInputElement) {
        radioToSelect.checked = true;
    }
}

function syncControlsWithPolicyState(rootElement) {
    if (!rootElement) {
        return;
    }

    const currentState = getSelectedAdmxState(rootElement);
    setControlsDisabledState(rootElement, currentState !== 'enabled');
}

function getControlElementByStoragePath(rootElement, storagePath = '') {
    if (!rootElement || !storagePath) {
        return null;
    }

    return rootElement.querySelector(`[data-storage-path="${CSS.escape(storagePath)}"]`);
}

function readControlValue(controlElement, metadata = {}) {
    if (!controlElement) {
        return null;
    }

    switch (metadata?.type) {
        case 'boolean': {
            const trueValue = Object.prototype.hasOwnProperty.call(metadata, 'trueValue')
                ? metadata.trueValue
                : true;
            const falseValue = Object.prototype.hasOwnProperty.call(metadata, 'falseValue')
                ? metadata.falseValue
                : false;

            return controlElement.checked ? trueValue : falseValue;
        }
        case 'decimal': {
            if (controlElement.value === '') {
                return null;
            }

            const parsedValue = Number(controlElement.value);
            return Number.isNaN(parsedValue) ? controlElement.value : parsedValue;
        }
        case 'list': {
            const raw = controlElement.value || '';
            if (raw === '') return [];
            return raw.split(',').map(s => s.trim()).filter(Boolean);
        }
        case 'enum':
        case 'text':
        default:
            return controlElement.value;
    }
}

function applyControlValue(controlElement, metadata = {}, value = null) {
    if (!controlElement || value === undefined) {
        return;
    }

    switch (metadata?.type) {
        case 'boolean': {
            const trueValue = Object.prototype.hasOwnProperty.call(metadata, 'trueValue')
                ? metadata.trueValue
                : true;

            controlElement.checked = value === true || String(value) === String(trueValue);
            return;
        }
        case 'list':
            controlElement.value = Array.isArray(value)
                ? value.join(',')
                : (value || '');
            return;
        case 'decimal':
        case 'enum':
        case 'text':
        default:
            controlElement.value = value ?? '';
    }
}

function buildAdmxFormSnapshot({ rootElement, controlEntries = [] } = {}) {
    return {
        state: getSelectedAdmxState(rootElement),
        controls: controlEntries.map(({ storagePath, metadata }) => {
            const controlElement = getControlElementByStoragePath(rootElement, storagePath);

            return {
                path: storagePath,
                type: metadata?.type ?? '',
                value: readControlValue(controlElement, metadata),
            };
        }),
    };
}

function applyAdmxFormSnapshot({ rootElement, snapshot = null, controlEntries = [] } = {}) {
    if (!rootElement || !snapshot) {
        return;
    }

    setSelectedAdmxState(rootElement, snapshot.state);

    const snapshotEntries = new Map(
        Array.isArray(snapshot.controls)
            ? snapshot.controls.map((entry) => [entry.path, entry])
            : []
    );

    controlEntries.forEach(({ storagePath, metadata }) => {
        const snapshotEntry = snapshotEntries.get(storagePath);

        if (!snapshotEntry) {
            return;
        }

        const controlElement = getControlElementByStoragePath(rootElement, storagePath);
        applyControlValue(controlElement, metadata, snapshotEntry.value);
    });

    syncControlsWithPolicyState(rootElement);
}

function applyDefaultValuesToAdmxForm({ rootElement, controlEntries = [] } = {}) {
    if (!rootElement) {
        return;
    }

    setSelectedAdmxState(rootElement, ADMX_DEFAULT_STATE);

    controlEntries.forEach(({ storagePath, metadata }) => {
        const controlElement = getControlElementByStoragePath(rootElement, storagePath);
        applyControlValue(controlElement, metadata, getDefaultControlValue(metadata));
    });

    syncControlsWithPolicyState(rootElement);
}

    return {
        setControlsDisabledState,
        getSelectedAdmxState,
        setSelectedAdmxState,
        syncControlsWithPolicyState,
        getControlElementByStoragePath,
        readControlValue,
        applyControlValue,
        buildAdmxFormSnapshot,
        applyAdmxFormSnapshot,
        applyDefaultValuesToAdmxForm,
    };
});
