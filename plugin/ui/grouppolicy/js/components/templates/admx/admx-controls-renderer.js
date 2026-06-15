define(['../../../util/element-creator', './admx-policy-normalizers'], function(__dep0, __dep1) {
var { createElement } = __dep0;
var { getEnumDefaultValue } = __dep1;

function formatExplainText(explainText = '') {
    return explainText
        .split(/\r?\n/)
        .flatMap((line, index, lines) => (index < lines.length - 1 ? [line, createElement('br')] : [line]));
}

function createCommonControlAttrs({ metadata = {}, policyPath = '', storagePath = '', type = '', isDisabled = true } = {}) {
    return {
        name: metadata.id ?? metadata.valueName ?? 'admx-control',
        disabled: isDisabled ? 'disabled' : null,
        'data-policy-path': policyPath,
        'data-storage-path': storagePath || policyPath,
        'data-policy-type': type,
    };
}

function renderUnsupportedControl() {
    return createElement('div', {
        className: 'field__element',
        text: 'В разработке'
    });
}

function renderListControl({ metadata = {}, policyPath = '', storagePath = '', isDisabled = true } = {}) {
    return createElement('div', {
        className: 'field__element',
        children: [
            createElement('input', {
                attrs: {
                    ...createCommonControlAttrs({
                        metadata,
                        policyPath,
                        storagePath,
                        type: 'list',
                        isDisabled: false,
                    }),
                    type: 'hidden',
                    value: '',
                }
            }),
            createElement('button', {
                className: ['btn', 'packages-control__btn-edit'],
                attrs: {
                    type: 'button',
                    disabled: isDisabled ? 'disabled' : null,
                    'data-storage-path': storagePath || policyPath,
                },
                text: 'Редактировать',
            })
        ]
    });
}

function renderEnumControl({ metadata = {}, policyPath = '', storagePath = '', isDisabled = true } = {}) {
    const items = metadata.items ?? {};
    const selectedValue = getEnumDefaultValue(items, metadata.defaultItem);
    const optionEntries = Object.entries(items);

    return createElement('div', {
        className: 'field__element',
        children: [
            createElement('select', {
                attrs: createCommonControlAttrs({
                    metadata,
                    policyPath,
                    storagePath,
                    type: 'enum',
                    isDisabled
                }),
                children: optionEntries.map(([value, label]) => createElement('option', {
                    attrs: {
                        value,
                        selected: value === selectedValue ? 'selected' : null
                    },
                    text: label
                }))
            })
        ]
    });
}

function renderBooleanControl({ metadata = {}, policyPath = '', storagePath = '', isDisabled = true } = {}) {
    return createElement('div', {
        className: 'field__element',
        children: [
            createElement('input', {
                attrs: {
                    ...createCommonControlAttrs({
                        metadata,
                        policyPath,
                        storagePath,
                        type: 'boolean',
                        isDisabled
                    }),
                    type: 'checkbox'
                }
            })
        ]
    });
}

function renderDecimalControl({ metadata = {}, policyPath = '', storagePath = '', isDisabled = true } = {}) {
    return createElement('div', {
        className: 'field__element',
        children: [
            createElement('input', {
                attrs: {
                    ...createCommonControlAttrs({
                        metadata,
                        policyPath,
                        storagePath,
                        type: 'decimal',
                        isDisabled
                    }),
                    type: 'number',
                    min: metadata.minValue ?? null,
                    max: metadata.maxValue ?? null,
                    value: metadata.defaultValue ?? null
                }
            })
        ]
    });
}

function renderTextControl({ metadata = {}, policyPath = '', storagePath = '', isDisabled = true } = {}) {
    return createElement('div', {
        className: 'field__element',
        children: [
            createElement('input', {
                attrs: {
                    ...createCommonControlAttrs({
                        metadata,
                        policyPath,
                        storagePath,
                        type: 'text',
                        isDisabled
                    }),
                    type: 'text'
                }
            })
        ]
    });
}

function renderControlByType({ metadata = {}, policyPath = '', storagePath = '', isDisabled = true } = {}) {
    const type = metadata?.type;

    switch (type) {
        case 'enum':
            return renderEnumControl({ metadata, policyPath, storagePath, isDisabled });
        case 'boolean':
            return renderBooleanControl({ metadata, policyPath, storagePath, isDisabled });
        case 'decimal':
            return renderDecimalControl({ metadata, policyPath, storagePath, isDisabled });
        case 'text':
            return renderTextControl({ metadata, policyPath, storagePath, isDisabled });
        case 'list':
            return renderListControl({ metadata, policyPath, storagePath, isDisabled });
        default:
            return renderUnsupportedControl();
    }
}

function renderAdmxControlRow({ metadata = {}, policyPath = '', storagePath = '', isDisabled = true } = {}) {
    return createElement('div', {
        className: 'gp__admx-item',
        children: [
            createElement('div', {
                className: 'gp__admx-description',
                text: metadata.label ?? ''
            }),
            createElement('div', {
                className: 'gp__admx-options',
                children: [
                    renderControlByType({ metadata, policyPath, storagePath, isDisabled })
                ]
            })
        ]
    });
}

    return {
        formatExplainText,
        createCommonControlAttrs,
        renderUnsupportedControl,
        renderListControl,
        renderEnumControl,
        renderBooleanControl,
        renderDecimalControl,
        renderTextControl,
        renderControlByType,
        renderAdmxControlRow,
    };
});
