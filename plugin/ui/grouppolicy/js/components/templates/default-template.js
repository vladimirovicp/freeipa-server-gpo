define(['../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


/**
 * Рендерит шаблон по умолчанию, когда шаблон не определен
 * @returns {ElementCreator} - Элемент с сообщением о том, что шаблон не определен
 */
function renderDefaultTemplate() {
    const defaultTemplate = createElement('div', {
        className: 'gp__default-template',
        children: [
            createElement('div', {
                className: 'default-template__message',
                text: 'Шаблон не определен'
            })
        ]
    });

    return defaultTemplate;
}
    return { renderDefaultTemplate };
});
