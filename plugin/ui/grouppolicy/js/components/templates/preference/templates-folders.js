define(['../../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


/**
 * Рендерит шаблон folders
 * @returns {ElementCreator} - Элемент с сообщением о том, что шаблон в процессе реализации
 */
function renderFoldersTemplate() {
    const foldersTemplate = createElement('div', {
        className: 'gp__default-template',
        children: [
            createElement('div', {
                className: 'default-template__message',
                text: 'Шаблон folders в процессе реализации'
            })
        ]
    });

    return foldersTemplate;
}
    return { renderFoldersTemplate };
});
