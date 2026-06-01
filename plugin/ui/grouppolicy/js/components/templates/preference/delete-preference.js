define(['../../../util/mainLocalStorage/shortcuts', './shortcuts/preferences-table-shortcuts'], function(__dep0, __dep1) {
var { getShortcutsFromLocalStorage, saveShortcutsToLocalStorage } = __dep0;
var { renderPreferencesTableShortcuts } = __dep1;


/**
 * Удаляет запись из localStorage по имени (data-preferences-name) и индексу (data-preferences-index).
 * Перерисовывает таблицу preference__table.
 * @param {HTMLElement} buttonEl - Кнопка .preferences__btn-delete с атрибутами data-preferences-name и data-preferences-index
 * @param {HTMLElement} [workspaceEl] - Элемент workspace для поиска контейнера таблицы
 */
function handleDeletePreference(buttonEl, workspaceEl) {
    if (!buttonEl) return;

    const preferencesName = buttonEl.getAttribute('data-preferences-name');
    const indexAttr = buttonEl.getAttribute('data-preferences-index');

    if (!preferencesName || indexAttr === null || indexAttr === '') return;

    const index = parseInt(indexAttr, 10);
    if (Number.isNaN(index) || index < 0) return;

    if (preferencesName === 'shortcuts') {
        const list = getShortcutsFromLocalStorage();
        if (index >= list.length) return;

        list.splice(index, 1);
        saveShortcutsToLocalStorage(list);
    } else {
        // Для других типов настроек — можно расширить при необходимости
        return;
    }

    refreshPreferencesTable(workspaceEl);

    // Сбрасываем атрибуты кнопки, если записей больше не осталось
    if (preferencesName === 'shortcuts' && getShortcutsFromLocalStorage().length === 0) {
        buttonEl.classList.remove('active');
        buttonEl.removeAttribute('data-preferences-index');
    }
}

/**
 * Перерисовывает таблицу preference__table в контейнере preference__data-table
 * @param {HTMLElement} [workspaceEl] - Элемент workspace (или его DOM-нода)
 */
function refreshPreferencesTable(workspaceEl) {
    const workspace = workspaceEl?.getElement ? workspaceEl.getElement() : workspaceEl;
    const container = workspace
        ? workspace.querySelector('.preference__data-table')
        : document.querySelector('.workspace .preference__data-table');

    if (!container) return;

    container.innerHTML = '';
    const table = renderPreferencesTableShortcuts();
    container.appendChild(table.getElement ? table.getElement() : table);
}
    return { handleDeletePreference };
});
