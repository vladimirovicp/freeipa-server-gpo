define(['../../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


/**
 * Рендерит шаблон networkShares
 * @returns {ElementCreator} - Элемент с сообщением о том, что шаблон в процессе реализации
 */
function renderNetworkSharesTemplate() {
    const networkSharesTemplate = createElement('div', {
        className: 'gp__default-template',
        children: [
            createElement('div', {
                className: 'default-template__message',
                text: 'Шаблон networkShares в процессе реализации'
            })
        ]
    });

    return networkSharesTemplate;
}
    return { renderNetworkSharesTemplate };
});
