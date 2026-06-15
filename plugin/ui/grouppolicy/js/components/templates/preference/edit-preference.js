define(['../../../util/mainLocalStorage/shortcuts', './create-preference', '../../../util/form-utils'], function(__dep0, __dep1, __dep2) {
var { getShortcutsFromLocalStorage } = __dep0;
var { resetActiveTabToBasic } = __dep1;
var { getValueElement, getFieldValue } = __dep2;


/**
 * Устанавливает значение в элемент поля.
 * @param {HTMLElement} fieldEl - контейнер поля с data-name
 * @param {string|number|boolean} value - значение для установки
 */
function setFieldValue(fieldEl, value) {
    const element = getValueElement(fieldEl);
    if (!element) return;

    const tagName = element.tagName.toLowerCase();
    const type = (element.type || '').toLowerCase();

    if (tagName === 'select') {
        element.value = String(value);
        return;
    }
    if (tagName === 'input' && (type === 'checkbox' || type === 'radio')) {
        element.checked = Boolean(value);
        return;
    }
    if (tagName === 'input' || tagName === 'textarea') {
        element.value = value === undefined || value === null ? '' : String(value);
    }
}

/**
 * Загружает данные из localStorage по ключу и индексу из модалки.
 * @param {HTMLElement} modalEl - элемент .preference__modal с data-preferences-name и при необходимости data-preferences-index
 * @returns {Record<string, string|number|boolean>|null}
 */
function getStoredPreferenceData(modalEl) {
    if (!modalEl) return null;

    const storageKey = modalEl.getAttribute('data-preferences-name');
    if (!storageKey) return null;

    if (storageKey === 'shortcuts') {
        const list = getShortcutsFromLocalStorage();
        const indexAttr = modalEl.getAttribute('data-preferences-index');
        const index = indexAttr !== null && indexAttr !== '' ? parseInt(indexAttr, 10) : -1;
        if (index >= 0 && index < list.length) return list[index];
        return null;
    }

    

    try {
        const raw = localStorage.getItem(storageKey);
        return raw ? JSON.parse(raw) : null;
    } catch (_) {
        return null;
    }
}

/**
 * Сравнивает данные из #tab-basic (и при необходимости #tab-general) с данными из localStorage
 * и исправляет значения полей, если они не соответствуют сохранённым.
 * @param {HTMLElement} modalEl - элемент .preference__modal (должен иметь data-preferences-name и при необходимости data-preferences-index)
 */
function syncModalFromStoredData(modalEl) {
    if (!modalEl) return;

    const stored = getStoredPreferenceData(modalEl);
    if (!stored || typeof stored !== 'object') return;

    const basicData = stored.basic ?? stored;
    const commonData = stored.common ?? stored;

    const tabBasic = modalEl.querySelector('#tab-basic');
    if (tabBasic) {
        tabBasic.querySelectorAll('[data-name]').forEach((fieldEl) => {
            const name = fieldEl.getAttribute('data-name');
            if (!name || !(name in basicData)) return;
            const valueEl = getValueElement(fieldEl);
            if (!valueEl) return;

            const current = getFieldValue(fieldEl);
            const needed = basicData[name];

            const currentNorm = typeof current === 'boolean' ? current : (current === undefined || current === null ? '' : String(current));
            const neededNorm = typeof needed === 'boolean' ? needed : (needed === undefined || needed === null ? '' : String(needed));

            if (currentNorm !== neededNorm) {
                setFieldValue(fieldEl, needed);
            }
        });
    }

    const tabGeneral = modalEl.querySelector('#tab-general');
    if (tabGeneral) {
        tabGeneral.querySelectorAll('[data-name]').forEach((fieldEl) => {
            const name = fieldEl.getAttribute('data-name');
            if (!name || !(name in commonData)) return;
            const valueEl = getValueElement(fieldEl);
            if (!valueEl) return;

            const current = getFieldValue(fieldEl);
            const needed = commonData[name];

            const currentNorm = typeof current === 'boolean' ? current : (current === undefined || current === null ? '' : String(current));
            const neededNorm = typeof needed === 'boolean' ? needed : (needed === undefined || needed === null ? '' : String(needed));

            if (currentNorm !== neededNorm) {
                setFieldValue(fieldEl, needed);
            }
        });
    }
}

/**
 * Открывает модальное окно в режиме редактирования: копирует data-атрибуты с кнопки в модалку,
 * затем синхронизирует форму с данными из localStorage (сравнивает и исправляет при несоответствии).
 * Вызывать после того, как в #tab-basic уже вставлен шаблон по умолчанию (как при preferences__btn-create).
 * @param {HTMLElement} btnEdit - кнопка .preferences__btn-edit
 * @param {HTMLElement} modalEl - элемент .preference__modal
 */
function openModalForEdit(btnEdit, modalEl) {
    if (!btnEdit || !modalEl) return;

    const name = btnEdit.getAttribute('data-preferences-name');
    const index = btnEdit.getAttribute('data-preferences-index');

    if (name != null) modalEl.setAttribute('data-preferences-name', name);
    if (index != null) modalEl.setAttribute('data-preferences-index', index);
    else modalEl.removeAttribute('data-preferences-index');
    modalEl.setAttribute('data-preferences-mode', 'edit');

    resetActiveTabToBasic(modalEl);
    syncModalFromStoredData(modalEl);
    modalEl.classList.add('active');
}
    return { syncModalFromStoredData, openModalForEdit };
});
