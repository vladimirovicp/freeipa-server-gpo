define([], function() {
/**
 * Получает элемент ввода (input, select, textarea, checkbox) внутри контейнера поля.
 * @param {HTMLElement} fieldEl - контейнер поля с data-name
 * @returns {HTMLElement|null} - найденный элемент ввода или null
 */
function getValueElement(fieldEl) {
    return fieldEl.querySelector('.field__element input, .field__element select, .field__element textarea')
        || fieldEl.querySelector('input[type="checkbox"], input[type="radio"]');
}

/**
 * Получает значение из элемента поля (input, select, textarea, checkbox).
 * @param {HTMLElement} fieldEl - контейнер поля с data-name
 * @returns {string|number|boolean} - значение поля
 */
function getFieldValue(fieldEl) {
    const element = getValueElement(fieldEl);
    if (!element) return '';

    const tagName = element.tagName.toLowerCase();
    const type = (element.type || '').toLowerCase();

    if (tagName === 'select') {
        return element.value;
    }
    if (tagName === 'input' && (type === 'checkbox' || type === 'radio')) {
        return element.checked;
    }
    if (tagName === 'input' && type === 'number') {
        const v = element.value;
        return v === '' ? '' : Number(v);
    }
    return element.value;
}
    return { getValueElement, getFieldValue };
});
