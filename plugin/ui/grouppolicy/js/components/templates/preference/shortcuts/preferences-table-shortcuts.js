define(['../../../../util/element-creator', '../../../../util/mainLocalStorage/shortcuts'], function(__dep0, __dep1) {
var { createElement } = __dep0;
var { getShortcutsFromLocalStorage } = __dep1;


const ACTION_LABELS = { 0: 'Создать', 1: 'Заменить', 2: 'Обновить', 3: 'Удалить' };

/**
 * Создаёт элементы настроек для блока .preference__settings-data
 * @param {Object} common - Объект с данными common (stopOnErrorCheckBox, userContextCheckBox, removeThisCheckBox)
 * @returns {Array<HTMLElement>} - Массив DOM-элементов
 */
function renderSettingsItems(common) {
    const bool = (val) => val ? 'Да' : 'Нет';
    const item = (label, value, empty = false) => createElement('div', {
        className: empty ? ['preference__settings-item', 'empty'] : 'preference__settings-item',
        children: [
            createElement('div', { text: label }),
            createElement('div', { text: value })
        ]
    }).getElement();

    return [
        item('Не обрабатывать элементы в расширении при ошибке:', bool(common.stopOnErrorCheckBox)),
        item('Запускать в контексте пользователя:', bool(common.userContextCheckBox)),
        item('Удалить, если не применимо:', bool(common.removeThisCheckBox)),
        item('Применить один раз:', 'Нет', true),
        item('Отфильтровано:', 'Нет', true),
        item('Отключено:', 'Нет', true),
        item('Отключено уровнем выше:', 'Нет', true),
    ];
}

/**
 * Обновляет блок .preference__info данными из записи с указанным индексом
 * @param {HTMLElement} preferenceRoot - Корневой элемент .gp__preference
 * @param {number} index - Индекс записи в localStorage
 */
function updatePreferenceInfo(preferenceRoot, index) {
    if (!preferenceRoot) return;
    const shortcuts = getShortcutsFromLocalStorage();
    if (index == null || !shortcuts[index]) return;
    const common = shortcuts[index].common;

    const descriptionEl = preferenceRoot.querySelector('.preference__description-data');
    if (descriptionEl) {
        descriptionEl.textContent = common.description ?? '';
    }

    const settingsEl = preferenceRoot.querySelector('.preference__settings-data');
    if (settingsEl) {
        settingsEl.innerHTML = '';
        renderSettingsItems(common).forEach(el => settingsEl.appendChild(el));
    }
}

/**
 * Создаёт строку таблицы ярлыков
 * @param {Object} row - Данные строки (SHORTCUT_PATH, order, ACTION, TARGET_PATH или name, action, value)
 * @param {boolean} [active] - Активная строка
 * @param {string} [namePreference='shortcuts'] - Имя таблицы предпочтений
 * @returns {ElementCreator}
 */
function createTableRow(row, active = false, namePreference = 'shortcuts') {
    const name = row.SHORTCUT_PATH ?? row.name ?? '';
    const order = row.order ?? '';
    const actionText = row.ACTION != null
        ? (typeof row.ACTION === 'number' ? ACTION_LABELS[row.ACTION] : row.ACTION)
        : (row.action ?? '');
    const target = row.TARGET_PATH ?? row.value ?? '';
    return createElement('tr', {
        className: active ? 'active' : undefined,
        events: {
            click: (event) => {
                const tbody = event.currentTarget.closest('tbody');
                if (tbody) {
                    tbody.querySelectorAll('tr').forEach((tr) => tr.classList.remove('active'));
                    event.currentTarget.classList.add('active');
                }
                
                // Получаем данные common текущей записи по индексу "Очерёдность"
                const orderIndex = row.order;
                const preferenceRoot = event.currentTarget.closest('.gp__preference');
                updatePreferenceInfo(preferenceRoot, orderIndex);
                
                document.dispatchEvent(new CustomEvent('preferences-row-select', { detail: { index: row.order } }));
            }
        },
        children: [
            createElement('td', { text: String(name) }),
            createElement('td', { text: String(order) }),
            createElement('td', { text: String(actionText) }),
            createElement('td', { text: String(target) })
        ]
    });
}

/**
 * Рендерит таблицу ярлыков (горячих клавиш)
 * @param {Array<Object>} [rows] - Данные строк таблицы
 * @param {number} [activeIndex=0] - Индекс строки, которой задать класс active
 * @param {string} [namePreference='shortcuts'] - Имя таблицы предпочтений
 * @returns {ElementCreator} - Элемент таблицы
 */
function renderPreferencesTableShortcuts(rows = [], activeIndex = 0, namePreference = 'shortcuts') {
    const shortcuts = getShortcutsFromLocalStorage();
    const basic = (item) => item.basic ?? item;
    const defaultRows = shortcuts.map((item, index) => ({
        SHORTCUT_PATH: basic(item).SHORTCUT_PATH ?? '',
        order: index,
        ACTION: basic(item).ACTION,
        TARGET_PATH: basic(item).TARGET_PATH ?? ''
    }));

    const dataRows = rows.length > 0 ? rows : defaultRows;

    if (dataRows.length === 0) {
        return createElement('div', {
            className: 'preference__data-table',
            children: [
                createElement('div', {
                    className: 'preference__data-empty',
                    children: [
                        createElement('div', {
                            className: 'preference__data-message',
                            text: 'В настоящий момент политик не добавлено'
                        })
                    ]
                })
            ]
        });
    }

    const safeActiveIndex = Math.max(0, Math.min(activeIndex, dataRows.length - 1));
    const tbodyRows = dataRows.map((row, index) =>
        createTableRow(row, index === safeActiveIndex, namePreference)
    );

    const table = createElement('table', {
        className: 'preference__table',
        children: [
            createElement('thead', {
                children: [
                    createElement('tr', {
                        children: [
                            createElement('th', { text: 'Имя' }),
                            createElement('th', { text: 'Очерёдность' }),
                            createElement('th', { text: 'Действие' }),
                            createElement('th', { text: 'Цель' }),
                        ]
                    })
                ]
            }),
            createElement('tbody', {
                children: tbodyRows
            })
        ]
    });

    document.dispatchEvent(new CustomEvent('preferences-row-select', { detail: { index: safeActiveIndex } }));

    // Автоматически заполняем .preference__info данными из записи с индексом safeActiveIndex
    setTimeout(() => {
        const preferenceRoot = table.getElement()?.closest('.gp__preference');
        if (preferenceRoot && dataRows.length > 0) {
            updatePreferenceInfo(preferenceRoot, safeActiveIndex);
        }
    }, 0);

    return table;
}
    return { renderPreferencesTableShortcuts };
});
