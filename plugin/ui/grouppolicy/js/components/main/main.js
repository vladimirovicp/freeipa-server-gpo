define(['../../util/element-creator', '../tree-view/tree-view', '../divider/divider', '../workspace/workspace'], function(__dep0, __dep1, __dep2, __dep3) {
var { createElement } = __dep0;
var { renderTreeView } = __dep1;
var { renderDivider } = __dep2;
var { renderWorkspace } = __dep3;


function renderMain(container, treeViewState) {
    const workspace = renderWorkspace();
    const treeView = renderTreeView(workspace, treeViewState);
    const divider = renderDivider();
    
    const main = createElement('div', {
        className: 'gp__main',
        children: [treeView, divider, workspace]
    });
    
    container.appendChild(main.getElement());
    return { main, treeView, divider, workspace };
}
    return { renderMain };
});
