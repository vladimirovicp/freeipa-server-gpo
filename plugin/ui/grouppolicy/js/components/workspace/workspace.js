define(['../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


function renderWorkspace() {
    const element = createElement('div', {
        className: 'workspace'
    });
    
    return element; // Возвращаем экземпляр ElementCreator для возможности использования его методов
}
    return { renderWorkspace };
});
