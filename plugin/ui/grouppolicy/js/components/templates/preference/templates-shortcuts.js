define(['./preferences-view-template', './shortcuts/preferences-table-shortcuts', '../../../util/mainLocalStorage/shortcuts'], function(__dep0, __dep1, __dep2) {
var { renderPreferencesTemplate } = __dep0;
var { renderPreferencesTableShortcuts } = __dep1;
var { getShortcutsFromLocalStorage } = __dep2;


/**
 * Рендерит шаблон shortcuts
 * @returns {ElementCreator} - Элемент с шаблоном preferences для shortcuts
 */
function renderShortcutsTemplate({ header } = {}) {
    return renderPreferencesTemplate({
        renderTable: renderPreferencesTableShortcuts,
        getDataFromStorage: getShortcutsFromLocalStorage,
        header,
        name: 'shortcuts',
    });
}
    return { renderShortcutsTemplate };
});
