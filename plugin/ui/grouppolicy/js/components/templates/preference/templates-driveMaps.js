define(['../../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


/**
 * Рендерит шаблон driveMaps
 * @returns {ElementCreator} - Элемент с сообщением о том, что шаблон в процессе реализации
 */
function renderDriveMapsTemplate() {
    const driveMapsTemplate = createElement('div', {
        className: 'gp__default-template',
        children: [
            createElement('div', {
                className: 'default-template__message',
                text: 'Шаблон driveMaps в процессе реализации'
            })
        ]
    });

    return driveMapsTemplate;
}
    return { renderDriveMapsTemplate };
});
