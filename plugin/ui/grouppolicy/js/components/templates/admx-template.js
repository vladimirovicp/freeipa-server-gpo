/**
 * admx-template.js — модуль рендеринга и управления ADMX-шаблоном групповой политики.
 *
 * Публичный API:
 *   - renderAdmxTemplate({ isHelpOpen, item, admxTreePath, header }) — главная точка входа.
 */
define([
    '../../util/element-creator',
    '../../locales/translations',
    './admx/admx-policy-normalizers',
    './admx/admx-controls-renderer',
    './admx/admx-template-controller',
], function(__dep0, __dep1, __dep2, __dep3, __dep4) {
var { createElement } = __dep0;
var { t } = __dep1;
var { normalizePolicyEntries } = __dep2;
var { formatExplainText, renderAdmxControlRow } = __dep3;
var { setupAdmxTemplateController, prepareAdmxInitialState } = __dep4;

async function renderAdmxTemplate({ isHelpOpen = false, item = {}, admxTreePath = null, header = null, isCurrent = null } = {}) {
    const effectiveTarget = item?.target ?? item?.policyData?.header?.class ?? item?.header?.class ?? '';

    const policyData = item.policyData ?? {};
    const policyHeader = policyData.header ?? {};
    const { controlEntries, policyValueEntry } = normalizePolicyEntries(policyData, policyHeader);

    const controlRows = controlEntries.map(({ metadata, policyPath, storagePath }) => renderAdmxControlRow({
        metadata,
        policyPath,
        storagePath,
        isDisabled: true
    }));

    const listEntries = controlEntries.filter(({ metadata }) => metadata?.type === 'list');

    const packagesModal = listEntries.length > 0
        ? createElement('div', {
            className: 'packages-control__modal',
            children: [
                createElement('div', {
                    className: 'packages-control__modal-wrapper',
                    children: [
                        createElement('div', {
                            className: 'packages-control__modal-header',
                            children: [
                                createElement('div', {
                                    className: 'title',
                                    text: listEntries[0].metadata?.label ?? ''
                                }),
                                createElement('div', {
                                    className: 'close'
                                })
                            ]
                        }),
                        createElement('div', {
                            className: 'packages-control__modal-content'
                        }),
                        createElement('div', {
                            className: 'packages-control__modal-footer',
                            children: [
                                createElement('div', {
                                    className: ['btn', 'btn-new'],
                                    text: 'New'
                                }),
                                createElement('div', {
                                    className: ['btn', 'btn-delete'],
                                    text: 'Delete'
                                }),
                                createElement('div', {
                                    className: ['btn', 'btn-cancel'],
                                    text: 'Cancel'
                                }),
                                createElement('div', {
                                    className: ['btn', 'btn-ok'],
                                    text: 'OK'
                                })
                            ]
                        })
                    ]
                })
            ]
        })
        : null;

    const admxTemplate = createElement('div', {
        className: 'gp__admx-wrapper',
        children: [
            createElement('div', {
                className: 'gp__admx',
                children: [
                    createElement('div', {
                        className: 'gp__admx-settings',
                        children: [
                            createElement('div', {
                                className: 'title',
                                children: [
                                    t('policies.policy') + ' ',
                                    createElement('span', {
                                        className: 'title__name',
                                        text: policyHeader.displayName ?? ''
                                    })
                                ]
                            }),
                            createElement('div', {
                                className: 'gp__admx-state-policy-title',
                                text: t('policies.policyState')
                            }),
                            createElement('div', {
                                className: 'gp__admx-state-policy',
                                attrs: {
                                    'data-policy-path': policyValueEntry?.policyPath ?? null,
                                    'data-enabled-value': policyValueEntry?.metadata?.enabledValue ?? null,
                                    'data-disabled-value': policyValueEntry?.metadata?.disabledValue ?? null,
                                },
                                children: [
                                    createElement('label', {
                                        className: 'gp__admx-radio',
                                        children: [
                                            createElement('input', {
                                                attrs: {
                                                    type: 'radio',
                                                    name: 'admx-state',
                                                    value: 'not-configured',
                                                    checked: 'checked'
                                                }
                                            }),
                                            createElement('span', {
                                                text: t('policies.notConfigured')
                                            })
                                        ]
                                    }),
                                    createElement('label', {
                                        className: 'gp__admx-radio',
                                        children: [
                                            createElement('input', {
                                                attrs: {
                                                    type: 'radio',
                                                    name: 'admx-state',
                                                    value: 'enabled'
                                                }
                                            }),
                                            createElement('span', {
                                                text: t('policies.enabled')
                                            })
                                        ]
                                    }),
                                    createElement('label', {
                                        className: 'gp__admx-radio',
                                        children: [
                                            createElement('input', {
                                                attrs: {
                                                    type: 'radio',
                                                    name: 'admx-state',
                                                    value: 'disabled'
                                                }
                                            }),
                                            createElement('span', {
                                                text: t('policies.disabled')
                                            })
                                        ]
                                    })
                                ]
                            }),
                            createElement('div', {
                                className: 'field__line'
                            })
                        ]
                    }),
                    createElement('div', {
                        className: 'gp__admx-info',
                        children: [
                            ...(controlRows.length > 0 ? [
                                createElement('div', {
                                    className: 'gp__admx-item',
                                    children: [
                                        createElement('div', {
                                            className: 'gp__admx-description',
                                            text: t('common.description')
                                        }),
                                        createElement('div', {
                                            className: 'gp__admx-options',
                                            text: t('common.options')
                                        })
                                    ]
                                }),
                                ...controlRows
                            ] : [])
                        ]
                    })
                ]
            }),
            createElement('div', {
                className: ['gp__admx-help', isHelpOpen ? 'is-open' : null],
                children: [
                    createElement('div', {
                        className: 'gp__admx-supported',
                        children: [
                            createElement('div', {
                                className: 'title',
                                text: t('policies.supportedOn')
                            }),
                            createElement('div', {
                                className: 'gp__admx-content',
                                text: policyHeader.supportedOn ?? ''
                            })
                        ]
                    }),
                    createElement('div', {
                        className: 'gp__admx-comment',
                        children: [
                            createElement('div', {
                                className: 'title',
                                text: t('common.comment')
                            }),
                            createElement('textarea', {
                                attrs: {
                                    name: 'comment'
                                }
                            })
                        ]
                    }),
                    createElement('div', {
                        className: 'gp__admx-text-help',
                        children: [
                            createElement('div', {
                                className: 'title',
                                text: t('common.help')
                            }),
                            createElement('div', {
                                className: 'gp__admx-content',
                                children: formatExplainText(policyHeader.explainText)
                            })
                        ]
                    })
                ]
            }),
            ...(packagesModal ? [packagesModal] : [])
        ]
    });

    const admxTemplateElement = admxTemplate.getElement();
    const statePolicyElement = admxTemplateElement.querySelector('.gp__admx-state-policy');
    const initialFormSnapshot = await prepareAdmxInitialState({
        rootElement: admxTemplateElement,
        controlEntries,
        effectiveTarget,
    });

    if (typeof isCurrent === 'function' && !isCurrent()) {
        admxTemplate.cleanup = () => {};
        return admxTemplate;
    }

    setupAdmxTemplateController({
        admxTemplate,
        admxTemplateElement,
        statePolicyElement,
        header,
        effectiveTarget,
        controlEntries,
        policyValueEntry,
        initialFormSnapshot,
    });

    return admxTemplate;
}

    return { renderAdmxTemplate };
});
