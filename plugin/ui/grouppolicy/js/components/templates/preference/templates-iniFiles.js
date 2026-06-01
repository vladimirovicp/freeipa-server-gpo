define(['../../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


/**
 * Рендерит шаблон iniFiles
 * @returns {ElementCreator} - Элемент с сообщением о том, что шаблон в процессе реализации
 */
function renderIniFilesTemplate() {
    const iniFilesTemplate = createElement('div', {
        className: 'gp__default-template',
        children: [
            createElement('div', {
                className: 'default-template__message',
                text: 'Шаблон iniFiles в процессе реализации'
            })
        ]
    });

    return iniFilesTemplate;
}
    return { renderIniFilesTemplate };
});
