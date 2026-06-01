define(['../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


function renderDivider() {
    const dividerLine = createElement('div', {
        className: 'divider__line'
    });
    
    const element = createElement('div', {
        className: 'divider',
        children: [dividerLine]
    });
    
    return element; // Возвращаем экземпляр ElementCreator для возможности использования его методов
}
    return { renderDivider };
});
