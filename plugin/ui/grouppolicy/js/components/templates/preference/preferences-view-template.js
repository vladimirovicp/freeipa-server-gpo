define(['../../../util/element-creator', '../../../util/resizable', '../../workspace/preferences-template-common', './create-preference', './delete-preference', './edit-preference'], function(__dep0, __dep1, __dep2, __dep3, __dep4, __dep5) {
var { createElement } = __dep0;
var { resizable } = __dep1;
var { renderPreferencesCommonTemplate } = __dep2;
var { savePreferencesFromModal, resetModalFormToDefaults, setModalCreateMode } = __dep3;
var { handleDeletePreference } = __dep4;
var { openModalForEdit } = __dep5;


function addManagedEventListener(cleanups, target, eventName, handler, options) {
    if (!target || typeof target.addEventListener !== 'function' || typeof handler !== 'function') {
        return;
    }

    target.addEventListener(eventName, handler, options);
    cleanups.push(() => target.removeEventListener(eventName, handler, options));
}

function clearHeaderButtonState({ btnCreate, btnEdit, btnDelete } = {}) {
    [btnCreate, btnEdit, btnDelete]
        .filter(Boolean)
        .forEach((buttonEl) => buttonEl.classList.remove('active'));

    [btnCreate, btnEdit, btnDelete]
        .filter(Boolean)
        .forEach((buttonEl) => {
            buttonEl.removeAttribute('data-preferences-name');
            buttonEl.removeAttribute('data-preferences-index');
        });

    const headerEl = btnCreate?.closest('.gp__header')
        || btnEdit?.closest('.gp__header')
        || btnDelete?.closest('.gp__header');
    const controlActions = headerEl?.querySelector('.gp__control-actions');
    if (controlActions) controlActions.style.display = 'none';
    const control = headerEl?.querySelector('.gp__control');
    if (control) control.style.display = 'none';
}

function initHeaderButtons(header) {
    const headerEl = header?.getElement();
    const control = headerEl?.querySelector('.gp__control');
    if (control) control.style.display = 'flex';
    const btnCreate = control?.querySelector('.preferences__btn-create');
    const btnEdit = control?.querySelector('.preferences__btn-edit');
    const btnDelete = control?.querySelector('.preferences__btn-delete');

    if (btnCreate && !btnCreate.classList.contains('active')) {
        btnCreate.classList.add('active');
    }

    if (btnEdit) btnEdit.classList.remove('active');
    if (btnDelete) btnDelete.classList.remove('active');

    const controlActions = headerEl?.querySelector('.gp__control-actions');
    if (controlActions) controlActions.style.display = 'none';

    return { btnCreate, btnEdit, btnDelete };
}

function initButtonHandlers({
    btnCreate,
    btnEdit,
    btnDelete,
    preferenceModal,
    rootEl,
    name,
    renderTable,
    getDataFromStorage,
    cleanups,
}) {
    const handleRowSelect = (e) => {
        const index = e.detail.index;

        [btnEdit, btnDelete].forEach((btn) => {
            if (!btn) return;

            btn.setAttribute('data-preferences-index', String(index));
            if (name != null) {
                btn.setAttribute('data-preferences-name', name);
            }
        });

        if (btnEdit) btnEdit.classList.add('active');
        if (btnDelete) btnDelete.classList.add('active');
    };

    addManagedEventListener(cleanups, document, 'preferences-row-select', handleRowSelect);

    if (btnDelete) {
        const handleDelete = () => {
            if (!btnDelete.classList.contains('active')) {
                return;
            }

            handleDeletePreference(btnDelete, rootEl);

            const list = getDataFromStorage ? getDataFromStorage() : [];
            if (list.length === 0) {
                if (btnEdit) {
                    btnEdit.classList.remove('active');
                    btnEdit.removeAttribute('data-preferences-index');
                }

                btnDelete.classList.remove('active');
                btnDelete.removeAttribute('data-preferences-index');
            }
        };

        addManagedEventListener(cleanups, btnDelete, 'click', handleDelete);
    }

    if (btnEdit && preferenceModal) {
        const handleEdit = () => {
            if (!btnEdit.classList.contains('active')) {
                return;
            }

            if (name != null) {
                preferenceModal.setAttribute('data-preferences-name', name);
            }

            resetModalFormToDefaults(preferenceModal);
            openModalForEdit(btnEdit, preferenceModal);
        };

        addManagedEventListener(cleanups, btnEdit, 'click', handleEdit);
    }

    if (btnCreate && preferenceModal) {
        const handleCreate = () => {
            if (!btnCreate.classList.contains('active')) {
                return;
            }

            if (name != null) {
                preferenceModal.setAttribute('data-preferences-name', name);
            }

            resetModalFormToDefaults(preferenceModal);
            preferenceModal.removeAttribute('data-preferences-index');
            setModalCreateMode(preferenceModal);
            preferenceModal.classList.add('active');
        };

        addManagedEventListener(cleanups, btnCreate, 'click', handleCreate);
    }
}

function renderPreferencesTemplate({ renderTable, getDataFromStorage, header, name } = {}) {
    const headerButtons = initHeaderButtons(header);
    const { btnCreate, btnEdit, btnDelete } = headerButtons;
    const cleanups = [];

    if (name && btnCreate) {
        btnCreate.setAttribute('data-preferences-name', name);
    }

    const list = getDataFromStorage ? getDataFromStorage() : [];
    if (list.length > 0) {
        if (btnEdit) {
            btnEdit.classList.add('active');
            if (name) btnEdit.setAttribute('data-preferences-name', name);
            btnEdit.setAttribute('data-preferences-index', '0');
        }

        if (btnDelete) {
            btnDelete.classList.add('active');
            if (name) btnDelete.setAttribute('data-preferences-name', name);
            btnDelete.setAttribute('data-preferences-index', '0');
        }
    }

    const preference = createElement('div', {
        className: 'gp__preference',
        children: [
            createElement('div', {
                className: 'preference__info',
                children: [
                    createElement('div', {
                        className: 'preference__settings',
                        children: [
                            createElement('div', {
                                className: 'preference__settings-title',
                                text: 'Настройки:'
                            }),
                            createElement('div', {
                                className: 'preference__settings-data'
                            })
                        ]
                    }),
                    createElement('div', {
                        className: 'preference__description',
                        children: [
                            createElement('div', {
                                className: 'preference__description-title',
                                text: 'Описание:'
                            }),
                            createElement('div', {
                                className: ['preference__description-data', 'disable']
                            })
                        ]
                    })
                ]
            }),
            createElement('div', {
                className: 'preference__divider',
                children: [
                    createElement('div', {
                        className: 'divider__line'
                    })
                ]
            }),
            createElement('div', {
                className: 'preference__data-table',
                children: [
                    renderTable ? renderTable() : null
                ]
            }),
            createElement('div', {
                className: 'preference__modal',
                children: [
                    createElement('div', {
                        className: 'preference__modal-wrapper',
                        children: [
                            createElement('div', {
                                className: 'preference__modal-header',
                                children: [
                                    createElement('div', {
                                        className: 'title',
                                        text: 'Диалог настроек'
                                    }),
                                    createElement('div', {
                                        className: 'close',
                                        events: {
                                            click: (event) => {
                                                const modal = event.target.closest('.preference__modal');
                                                if (modal) {
                                                    resetModalFormToDefaults(modal);
                                                    modal.classList.remove('active');
                                                }
                                            }
                                        }
                                    })
                                ]
                            }),
                            createElement('div', {
                                className: 'preference__modal-content',
                                children: [
                                    createElement('div', {
                                        className: 'preference__modal-tabs',
                                        children: [
                                            createElement('div', {
                                                className: 'tab-buttons',
                                                children: [
                                                    createElement('div', {
                                                        className: ['preference__tab-button', 'active'],
                                                        attrs: {
                                                            'data-tab': 'tab-basic'
                                                        },
                                                        text: 'Основные настройки'
                                                    }),
                                                    createElement('div', {
                                                        className: ['preference__tab-button'],
                                                        attrs: {
                                                            'data-tab': 'tab-general'
                                                        },
                                                        text: 'Общие'
                                                    })
                                                ]
                                            }),
                                            createElement('div', {
                                                id: 'tab-basic',
                                                className: ['tab-content', 'active']
                                            }),
                                            createElement('div', {
                                                id: 'tab-general',
                                                className: ['tab-content'],
                                                children: [
                                                    renderPreferencesCommonTemplate()
                                                ]
                                            })
                                        ]
                                    })
                                ]
                            }),
                            createElement('div', {
                                className: 'preference__modal-footer',
                                children: [
                                    createElement('div', {
                                        className: ['btn', 'btn-cancel'],
                                        text: 'Отмена',
                                        events: {
                                            click: (event) => {
                                                const modal = event.target.closest('.preference__modal');
                                                if (modal) {
                                                    resetModalFormToDefaults(modal);
                                                    modal.classList.remove('active');
                                                }
                                            }
                                        }
                                    }),
                                    createElement('div', {
                                        className: ['btn', 'btn-ok'],
                                        text: 'Ок',
                                        events: {
                                            click: (event) => {
                                                const modal = event.target.closest('.preference__modal');
                                                if (!modal) return;

                                                const mode = modal.getAttribute('data-preferences-mode');
                                                if (mode !== 'create' && mode !== 'edit') {
                                                    return;
                                                }

                                                savePreferencesFromModal(modal);

                                                if (renderTable && getDataFromStorage) {
                                                    const preferenceRoot = modal.closest('.gp__preference');
                                                    const tableContainer = preferenceRoot?.querySelector('.preference__data-table');

                                                    if (tableContainer) {
                                                        const indexAttr = modal.getAttribute('data-preferences-index');
                                                        const currentList = getDataFromStorage();
                                                        const activeIndex = (indexAttr !== null && indexAttr !== '')
                                                            ? Math.min(parseInt(indexAttr, 10), currentList.length - 1)
                                                            : currentList.length - 1;

                                                        tableContainer.innerHTML = '';
                                                        tableContainer.appendChild(renderTable([], activeIndex).getElement());
                                                    }
                                                }

                                                modal.classList.remove('active');
                                            }
                                        }
                                    })
                                ]
                            })
                        ]
                    })
                ]
            })
        ]
    });

    const rootEl = preference.getElement();
    const basicTabButton = rootEl.querySelector('.preference__tab-button[data-tab="tab-basic"]');
    const generalTabButton = rootEl.querySelector('.preference__tab-button[data-tab="tab-general"]');
    const basicTabContent = rootEl.querySelector('#tab-basic');
    const generalTabContent = rootEl.querySelector('#tab-general');

    if (basicTabButton && generalTabButton && basicTabContent && generalTabContent) {
        const activateBasicTab = () => {
            if (basicTabButton.classList.contains('active')) {
                return;
            }

            basicTabButton.classList.add('active');
            basicTabContent.classList.add('active');
            generalTabButton.classList.remove('active');
            generalTabContent.classList.remove('active');
        };

        const activateGeneralTab = () => {
            if (generalTabButton.classList.contains('active')) {
                return;
            }

            generalTabButton.classList.add('active');
            generalTabContent.classList.add('active');
            basicTabButton.classList.remove('active');
            basicTabContent.classList.remove('active');
        };

        addManagedEventListener(cleanups, basicTabButton, 'click', activateBasicTab);
        addManagedEventListener(cleanups, generalTabButton, 'click', activateGeneralTab);
    }

    const dividerElement = rootEl.querySelector('.preference__divider');
    const infoElement = rootEl.querySelector('.preference__info');
    let cleanupPreferenceResizable = null;
    const frameId = requestAnimationFrame(() => {
        if (dividerElement && infoElement && rootEl) {
            cleanupPreferenceResizable = resizable(dividerElement, infoElement, rootEl, { minWidth: 100 });
        }
    });

    cleanups.push(() => {
        cancelAnimationFrame(frameId);

        if (typeof cleanupPreferenceResizable === 'function') {
            cleanupPreferenceResizable();
            cleanupPreferenceResizable = null;
        }
    });

    const preferenceModal = rootEl.querySelector('.preference__modal');

    initButtonHandlers({
        btnCreate,
        btnEdit,
        btnDelete,
        preferenceModal,
        rootEl,
        name,
        renderTable,
        getDataFromStorage,
        cleanups,
    });

    let cleanedUp = false;
    preference.cleanup = () => {
        if (cleanedUp) return;
        cleanedUp = true;

        while (cleanups.length > 0) {
            const cleanup = cleanups.pop();
            if (typeof cleanup === 'function') {
                cleanup();
            }
        }

        clearHeaderButtonState(headerButtons);
    };

    return preference;
}
    return { renderPreferencesTemplate };
});
