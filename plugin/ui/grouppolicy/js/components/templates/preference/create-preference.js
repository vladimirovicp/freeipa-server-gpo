define(['../../../util/mainLocalStorage/shortcuts', './shortcuts/preferences-template-shortcuts', '../../workspace/preferences-template-common', '../../../util/form-utils'], function(__dep0, __dep1, __dep2, __dep3) {
var { getShortcutsFromLocalStorage, saveShortcutsToLocalStorage, VALID_TARGET_TYPES } = __dep0;
var { renderPreferencesShortcutsTemplate } = __dep1;
var { renderPreferencesCommonTemplate } = __dep2;
var { getValueElement, getFieldValue } = __dep3;


/** Поля ярлыков, которые в localStorage хранятся как number */
const SHORTCUT_NUMBER_KEYS = ['ACTION', 'TARGET_TYPE', 'LOCATION', 'WINDOW', 'ICON_INDEX'];

/**
 * Собирает данные из вкладки #tab-basic: обходит элементы с data-name,
 * определяет ключ записи и берёт выбранное/введённое значение.
 * @param {HTMLElement} tabBasicEl - элемент #tab-basic
 * @returns {Record<string, string|number|boolean>} - объект { dataName: value }
 */
function collectPreferencesFromTabBasic(tabBasicEl) {
    if (!tabBasicEl) return {};

    const data = {};
    const fields = tabBasicEl.querySelectorAll('[data-name]');

    fields.forEach((fieldEl) => {
        const name = fieldEl.getAttribute('data-name');
        if (!name) return;
        // Пропускаем декоративные элементы (например field__line)
        const valueEl = getValueElement(fieldEl);
        if (!valueEl) return;
        data[name] = getFieldValue(fieldEl);
    });

    return data;
}

/**
 * Устанавливает режим модалки «создание» (data-preferences-mode="create").
 * Вызывать при открытии модалки по кнопке создания.
 * @param {HTMLElement} modalEl - элемент .preference__modal
 */
function setModalCreateMode(modalEl) {
    if (!modalEl) return;
    modalEl.setAttribute('data-preferences-mode', 'create');
}

/**
 * Переключает активную вкладку на tab-basic.
 * @param {HTMLElement} modalEl - элемент .preference__modal
 */
function resetActiveTabToBasic(modalEl) {
    if (!modalEl) return;
    const basicBtn = modalEl.querySelector('.preference__tab-button[data-tab="tab-basic"]');
    const generalBtn = modalEl.querySelector('.preference__tab-button[data-tab="tab-general"]');
    const basicContent = modalEl.querySelector('#tab-basic');
    const generalContent = modalEl.querySelector('#tab-general');

    if (basicBtn) basicBtn.classList.add('active');
    if (generalBtn) generalBtn.classList.remove('active');
    if (basicContent) basicContent.classList.add('active');
    if (generalContent) generalContent.classList.remove('active');
}

/**
 * Сбрасывает форму модалки к значениям по умолчанию: перерисовывает #tab-basic и #tab-general.
 * @param {HTMLElement} modalEl - элемент .preference__modal
 */
function resetModalFormToDefaults(modalEl) {
    if (!modalEl) return;
    resetActiveTabToBasic(modalEl);
    const preferencesName = modalEl.getAttribute('data-preferences-name');

    const tabBasic = modalEl.querySelector('#tab-basic');
    if (tabBasic && preferencesName === 'shortcuts') {
        tabBasic.innerHTML = '';
        const tpl = renderPreferencesShortcutsTemplate();
        if (tpl?.getElement) tabBasic.appendChild(tpl.getElement());
    }

    const tabGeneral = modalEl.querySelector('#tab-general');
    if (tabGeneral) {
        tabGeneral.innerHTML = '';
        const tpl = renderPreferencesCommonTemplate();
        if (tpl?.getElement) tabGeneral.appendChild(tpl.getElement());
    }
}

/**
 * Определяет ключ localStorage по модалке (data-preferences-name) и сохраняет
 * собранные данные в localStorage. Для "shortcuts" обновляет/добавляет элемент в массив.
 * @param {HTMLElement} modalEl - элемент .preference__modal
 */
function savePreferencesFromModal(modalEl) {
    if (!modalEl) return;

    const storageKey = modalEl.getAttribute('data-preferences-name');
    if (!storageKey) return;

    const tabBasic = modalEl.querySelector('#tab-basic');
    const tabGeneral = modalEl.querySelector('#tab-general');
    const basicData = collectPreferencesFromTabBasic(tabBasic);
    const commonData = collectPreferencesFromTabBasic(tabGeneral);
    if (Object.keys(basicData).length === 0) return;

    if (storageKey === 'shortcuts') {
        const normalizedBasic = { ...basicData };
        SHORTCUT_NUMBER_KEYS.forEach((key) => {
            if (key in normalizedBasic && normalizedBasic[key] !== '') {
                const n = Number(normalizedBasic[key]);
                normalizedBasic[key] = Number.isNaN(n) ? normalizedBasic[key] : n;
            }
        });
        /*
         * TARGET_TYPE: explicit validation, no silent coercion.
         * The form <select> only offers values in VALID_TARGET_TYPES {0, 1, 2},
         * so after Number() conversion the value is always valid for normal flow.
         * If an out-of-range value appears (legacy data loaded into form),
         * we warn explicitly — schema validation in saveShortcutsToLocalStorage
         * will reject the write. Legacy data needs a dedicated migration,
         * not a hidden clamp on save.
         */
        if ('TARGET_TYPE' in normalizedBasic) {
            const v = normalizedBasic.TARGET_TYPE;
            if (typeof v !== 'number' || !VALID_TARGET_TYPES.has(v)) {
                console.warn(
                    `[shortcuts] TARGET_TYPE has unexpected value: ${v}.`,
                    'Legacy data may need explicit migration.'
                );
            }
        }
        const normalizedCommon = { ...commonData };
        const list = getShortcutsFromLocalStorage();
        const indexAttr = modalEl.getAttribute('data-preferences-index');
        const index = indexAttr !== null && indexAttr !== '' ? parseInt(indexAttr, 10) : -1;
        const entry = { basic: normalizedBasic, common: normalizedCommon };
        if (index >= 0 && index < list.length) {
            list[index] = entry;
        } else {
            list.push(entry);
        }
        saveShortcutsToLocalStorage(list);
    } else {
        localStorage.setItem(storageKey, JSON.stringify(basicData));
    }
}
    return { collectPreferencesFromTabBasic, setModalCreateMode, resetActiveTabToBasic, resetModalFormToDefaults, savePreferencesFromModal };
});
