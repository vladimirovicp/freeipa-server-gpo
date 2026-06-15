define(['../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


/**
 * Рендерит общий шаблон настроек (чекбоксы и комментарий)
 * @returns {ElementCreator} - Элемент с шаблоном общих настроек
 */
function renderPreferencesCommonTemplate() {
    const container = createElement('div', {
        className: 'preferences-common',
        children: [
            createElement('div', {
                className: ['field', 'field__checkbox'],
                attrs: { 'data-name': 'stopOnErrorCheckBox' },
                children: [
                    createElement('label', {
                        children: [
                            createElement('input', {
                                attrs: {
                                    type: 'checkbox',
                                    name: 'stopOnErrorCheckBox_option'
                                }
                            }),
                            createElement('span', {
                                className: 'field__label-checkbox',
                                text: 'Остановить обработку элементов при ошибке'
                            })
                        ]
                    })
                ]
            }),
            createElement('div', {
                className: ['field', 'field__checkbox'],
                attrs: { 'data-name': 'userContextCheckBox' },
                children: [
                    createElement('label', {
                        children: [
                            createElement('input', {
                                attrs: {
                                    type: 'checkbox',
                                    name: 'userContextCheckBox_option'
                                }
                            }),
                            createElement('span', {
                                className: 'field__label-checkbox',
                                text: 'Выполнять в контексте безопасности текущего пользователя (опция пользовательских политик)'
                            })
                        ]
                    })
                ]
            }),
            createElement('div', {
                className: ['field', 'field__checkbox'],
                attrs: { 'data-name': 'removeThisCheckBox' },
                children: [
                    createElement('label', {
                        children: [
                            createElement('input', {
                                attrs: {
                                    type: 'checkbox',
                                    name: 'removeThisCheckBox_option'
                                }
                            }),
                            createElement('span', {
                                className: 'field__label-checkbox',
                                text: 'Удалить элемент, если больше не применим'
                            })
                        ]
                    })
                ]
            }),
            createElement('div', {
                className: ['field', 'field__checkbox'],
                attrs: { 'data-name': 'applyOnceCheckBox' },
                children: [
                    createElement('label', {
                        children: [
                            createElement('input', {
                                attrs: {
                                    type: 'checkbox',
                                    name: 'applyOnceCheckBox_option',
                                    disabled: 'disabled'
                                }
                            }),
                            createElement('span', {
                                className: 'field__label-checkbox',
                                text: 'Применить только один раз'
                            })
                        ]
                    })
                ]
            }),
            createElement('div', {
                className: ['field', 'field__checkbox'],
                attrs: { 'data-name': 'itemLevelCheckBox' },
                children: [
                    createElement('label', {
                        children: [
                            createElement('input', {
                                attrs: {
                                    type: 'checkbox',
                                    name: 'itemLevelCheckBox_option',
                                    disabled: 'disabled'
                                }
                            }),
                            createElement('span', {
                                className: 'field__label-checkbox',
                                text: 'Выбор элементов'
                            })
                        ]
                    })
                ]
            }),
            createElement('div', {
                className: ['field', 'field__description'],
                attrs: { 'data-name': 'description' },
                children: [
                    createElement('div', {
                        className: 'field__label',
                        text: 'Описание:'
                    }),
                    createElement('div', {
                        className: 'field__element',
                        children: [
                            createElement('textarea', {
                                attrs: {
                                    name: 'description'
                                }
                            })
                        ]
                    })
                ]
            })
        ]
    });

    return container;
}
    return { renderPreferencesCommonTemplate };
});
