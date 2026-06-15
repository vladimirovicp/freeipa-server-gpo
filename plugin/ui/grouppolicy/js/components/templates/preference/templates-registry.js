define(['../../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


/**
 * Рендерит шаблон registry
 * @returns {ElementCreator} - Элемент с сообщением о том, что шаблон в процессе реализации
 */
function renderRegistryTemplate() {
    const registryTemplate = createElement('div', {
        className: 'gp__default-template',
        children: [
            createElement('div', {
                className: 'default-template__message',
                text: 'Шаблон registry в процессе реализации'
            })
        ]
    });

    return registryTemplate;
}
    return { renderRegistryTemplate };
});
