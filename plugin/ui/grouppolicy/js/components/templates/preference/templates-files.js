define(['../../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


/**
 * Рендерит шаблон files
 * @returns {ElementCreator} - Элемент с сообщением о том, что шаблон в процессе реализации
 */
function renderFilesTemplate() {
    const filesTemplate = createElement('div', {
        className: 'gp__default-template',
        children: [
            createElement('div', {
                className: 'default-template__message',
                text: 'Шаблон files в процессе реализации'
            })
        ]
    });

    return filesTemplate;
}
    return { renderFilesTemplate };
});
