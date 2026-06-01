define(['../../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


/**
 * Рендерит шаблон environment
 * @returns {ElementCreator} - Элемент с сообщением о том, что шаблон в процессе реализации
 */
function renderEnvironmentTemplate() {
    const environmentTemplate = createElement('div', {
        className: 'gp__default-template',
        children: [
            createElement('div', {
                className: 'default-template__message',
                text: 'Шаблон environment в процессе реализации'
            })
        ]
    });

    return environmentTemplate;
}
    return { renderEnvironmentTemplate };
});
