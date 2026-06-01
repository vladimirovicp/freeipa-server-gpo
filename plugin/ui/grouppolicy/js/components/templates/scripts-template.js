define(['../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


/**
 * Рендерит рабочую область для политики «Скрипты» (Machine).
 * @returns {ElementCreator}
 */
function renderScriptsTemplate() {
    const defaultTemplate = createElement('div', {
        className: 'gp__default-template',
        children: [
            createElement('div', {
                className: 'default-template__message',
                text: 'Шаблон скрипта не реализован'
            })
        ]
    });

    return defaultTemplate;
}
    return { renderScriptsTemplate };
});
