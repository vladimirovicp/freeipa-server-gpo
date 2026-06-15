define(['../../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


/**
 * Рендерит шаблон shortcuts
 * @returns {ElementCreator} - Элемент с сообщением о том, что шаблон в процессе реализации
 */
function renderShortcutsTemplate() {
    const shortcutsTemplate = createElement('div', {
        className: 'gp__default-template',
        children: [
            createElement('div', {
                className: 'default-template__message',
                text: 'Шаблон shortcuts в процессе реализации'
            })
        ]
    });

    return shortcutsTemplate;
}
    return { renderShortcutsTemplate };
});
