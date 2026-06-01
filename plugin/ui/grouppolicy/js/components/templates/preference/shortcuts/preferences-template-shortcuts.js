define(['../../../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


/**
 * Рендерит шаблон настроек ярлыка (горячей клавиши)
 * @returns {ElementCreator} - Элемент с шаблоном настроек ярлыка
 */
function renderPreferencesShortcutsTemplate() {
    const container = createElement('div', {
        className: 'preferences-shortcuts',
        children: [
            // Действие
            createElement('div', {
                className: ['field', 'select'],
                attrs: {
                    'data-name': 'ACTION'
                },
                children: [
                    createElement('div', {
                        className: 'field__label',
                        text: 'Действие:'
                    }),
                    createElement('div', {
                        className: 'field__element',
                        children: [
                            createElement('select', {
                                attrs: {
                                    name: 'action'
                                },
                                children: [
                                    createElement('option', {
                                        attrs: {
                                            value: '0',
                                            selected: 'selected'
                                        },
                                        text: 'Создать'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '1'
                                        },
                                        text: 'Заменить'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '2'
                                        },
                                        text: 'Обновить'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '3'
                                        },
                                        text: 'Удалить'
                                    })
                                ]
                            })
                        ]
                    })
                ]
            }),

            // Линия
            createElement('div', {
                className: 'field__line'
            }),

            // Название
            createElement('div', {
                className: ['field', 'field__input', 'field__input--path'],
                attrs: {
                    'data-name': 'SHORTCUT_PATH'
                },
                children: [
                    createElement('div', {
                        className: 'field__label',
                        text: 'Название:'
                    }),
                    createElement('div', {
                        className: 'field__element',
                        children: [
                            createElement('input', {
                                attrs: {
                                    type: 'text',
                                }
                            })
                        ]
                    })
                ]
            }),

            // Тип цели
            createElement('div', {
                className: ['field', 'select'],
                attrs: {
                    'data-name': 'TARGET_TYPE'
                },
                children: [
                    createElement('div', {
                        className: 'field__label',
                        text: 'Тип цели:'
                    }),
                    createElement('div', {
                        className: 'field__element',
                        children: [
                            createElement('select', {
                                attrs: {
                                    name: 'targetType'
                                },
                                children: [
                                    createElement('option', {
                                        attrs: {
                                            value: '0',
                                            selected: 'selected'
                                        },
                                        text: 'Объект файловой системы'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '1'
                                        },
                                        text: 'URL-адрес'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '2'
                                        },
                                        text: 'Объект оболочки'
                                    })
                                ]
                            })
                        ]
                    })
                ]
            }),

            // Место нахождения
            createElement('div', {
                className: ['field', 'select'],
                attrs: {
                    'data-name': 'LOCATION'
                },
                children: [
                    createElement('div', {
                        className: 'field__label',
                        text: 'Место нахождения:'
                    }),
                    createElement('div', {
                        className: 'field__element',
                        children: [
                            createElement('select', {
                                children: [
                                    createElement('option', {
                                        attrs: {
                                            value: '0',
                                            selected: 'selected'
                                        },
                                        text: '[Укажите полный путь]'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '1'
                                        },
                                        text: 'Рабочий стол'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '2'
                                        },
                                        text: 'Стартовое меню'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '3'
                                        },
                                        text: 'Программы'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '4'
                                        },
                                        text: 'Запуск'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '5'
                                        },
                                        text: 'Избранное'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '6'
                                        },
                                        text: 'Ссылки'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '7'
                                        },
                                        text: 'Отправить'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '8'
                                        },
                                        text: 'Недавние'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '9'
                                        },
                                        text: 'Панель быстрого запуска'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '10'
                                        },
                                        text: 'Мои места в Сети'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '11'
                                        },
                                        text: 'Общий Рабочий стол'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '12'
                                        },
                                        text: 'Общее Стартовое меню'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '13'
                                        },
                                        text: 'Общие Программы'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '14'
                                        },
                                        text: 'Общий Запуск'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '15'
                                        },
                                        text: 'Общие Избранное'
                                    })
                                ]
                            })
                        ]
                    })
                ]
            }),

            // Линия
            createElement('div', {
                className: 'field__line'
            }),

            // Целевой путь
            createElement('div', {
                className: ['field', 'field__input', 'field__input--path'],
                attrs: {
                    'data-name': 'TARGET_PATH'
                },
                children: [
                    createElement('div', {
                        className: 'field__label',
                        text: 'Целевой путь:'
                    }),
                    createElement('div', {
                        className: 'field__element',
                        children: [
                            createElement('input', {
                                attrs: {
                                    type: 'text',
                                }
                            })
                        ]
                    })
                ]
            }),

            // Аргументы
            createElement('div', {
                className: ['field', 'field__input'],
                attrs: {
                    'data-name': 'ARGUMENTS'
                },
                children: [
                    createElement('div', {
                        className: 'field__label',
                        text: 'Аргументы:'
                    }),
                    createElement('div', {
                        className: 'field__element',
                        children: [
                            createElement('input', {
                                attrs: {
                                    type: 'text'
                                }
                            })
                        ]
                    })
                ]
            }),

            // Линия
            createElement('div', {
                className: 'field__line'
            }),

            // Путь к файлу значка
            createElement('div', {
                className: ['field', 'field__input', 'field__input--path'],
                attrs: {
                    'data-name': 'ICON_PATH'
                },
                children: [
                    createElement('div', {
                        className: 'field__label',
                        text: 'Путь к файлу значка:'
                    }),
                    createElement('div', {
                        className: 'field__element',
                        children: [
                            createElement('input', {
                                attrs: {
                                    type: 'text'
                                }
                            })
                        ]
                    })
                ]
            }),

            // Индекс значка
            createElement('div', {
                className: ['field', 'select'],
                attrs: {
                    'data-name': 'ICON_INDEX'
                },
                children: [
                    createElement('div', {
                        className: 'field__label',
                        text: 'Индекс значка:'
                    }),
                    createElement('div', {
                        className: 'field__element',
                        children: [
                            createElement('input', {
                                attrs: {
                                    type: 'number',
                                    disabled: 'disabled',
                                    value: '0'
                                }
                            })
                        ]
                    })
                ]
            }),

            // Линия
            createElement('div', {
                className: 'field__line'
            }),

            // Начинать
            createElement('div', {
                className: ['field', 'field__input', 'field__input--path'],
                attrs: {
                    'data-name': 'START_IN'
                },
                children: [
                    createElement('div', {
                        className: 'field__label',
                        text: 'Начинать:'
                    }),
                    createElement('div', {
                        className: 'field__element',
                        children: [
                            createElement('input', {
                                attrs: {
                                    type: 'text'
                                }
                            })
                        ]
                    })
                ]
            }),

            // Быстрая клавиша
            createElement('div', {
                className: ['field', 'field__input', 'field__input--hotkey'],
                attrs: {
                    'data-name': 'SHORTCUT_KEY'
                },
                children: [
                    createElement('div', {
                        className: 'field__label',
                        text: 'Быстрая клавиша:'
                    }),
                    createElement('div', {
                        className: 'field__element',
                        children: [
                            createElement('input', {
                                attrs: {
                                    type: 'text',
                                    placeholder: 'Введи комбинацию клавиш'
                                }
                            })
                        ]
                    })
                ]
            }),

            // Запуск
            createElement('div', {
                className: ['field', 'select'],
                attrs: {
                    'data-name': 'WINDOW'
                },
                children: [
                    createElement('div', {
                        className: 'field__label',
                        text: 'Запуск:'
                    }),
                    createElement('div', {
                        className: 'field__element',
                        children: [
                            createElement('select', {
                                attrs: {
                                    name: 'runMode'
                                },
                                children: [
                                    createElement('option', {
                                        attrs: {
                                            value: '0',
                                            selected: 'selected'
                                        },
                                        text: 'Обычное окно'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '1'
                                        },
                                        text: 'Свёрнутое'
                                    }),
                                    createElement('option', {
                                        attrs: {
                                            value: '2'
                                        },
                                        text: 'Увеличенное'
                                    })
                                ]
                            })
                        ]
                    })
                ]
            }),

            // Комментарий
            createElement('div', {
                className: ['field', 'field__comment'],
                attrs: {
                    'data-name': 'COMMENT'
                },
                children: [
                    createElement('div', {
                        className: 'field__label',
                        text: 'Комментарий:'
                    }),
                    createElement('div', {
                        className: 'field__element',
                        children: [
                            createElement('textarea', {
                                attrs: {
                                    name: 'comment'
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
    return { renderPreferencesShortcutsTemplate };
});
