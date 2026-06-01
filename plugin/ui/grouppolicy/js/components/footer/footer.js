define(['../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


function renderFooter(container) {
    const element = createElement('div', {
        className: 'gp__footer',
    });
    container.appendChild(element.getElement());
    return element.getElement();
}
    return { renderFooter };
});
