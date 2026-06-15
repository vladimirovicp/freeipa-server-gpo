define(['../../util/element-creator'], function(__dep0) {
var { createElement } = __dep0;


function setTreeItemActive(treeItemElement, container = document) {
    if (!treeItemElement) {
        return null;
    }

    container.querySelectorAll('.tree-item.active').forEach((currentTreeItem) => {
        if (currentTreeItem !== treeItemElement) {
            currentTreeItem.classList.remove('active');
        }
    });

    treeItemElement.classList.add('active');
    return treeItemElement;
}

function setFolderOpenedState(listItemElement, item, opened) {
    if (item?.type !== 'folder') {
        return Boolean(item?.opened);
    }

    if (!listItemElement) {
        item.opened = Boolean(opened);
        return item.opened;
    }

    const shouldOpen = Boolean(opened);
    const nestedList = listItemElement.querySelector(':scope > ul.tree-view__list');

    item.opened = shouldOpen;
    listItemElement.classList.toggle('opened', shouldOpen);
    listItemElement.classList.toggle('closed', !shouldOpen);

    if (nestedList) {
        nestedList.style.display = shouldOpen ? '' : 'none';
    }

    return shouldOpen;
}

function toggleFolder(listItemElement, item) {
    return setFolderOpenedState(listItemElement, item, !item?.opened);
}

function renderTreeItem(item, treeViewState, parentItem = null) {
    const classes = ['view'];

    if (item.type === 'folder') {
        classes.push('folder');
        classes.push(item.opened ? 'opened' : 'closed');
    } else {
        classes.push('file');
    }

    const treeItem = createElement('span', {
        className: 'tree-item',
        children: []
    });

    if (item.type === 'folder') {
        treeItem.append(createElement('span', {
            className: 'icon-switcher'
        }));
    }

    if (item.icon) {
        treeItem.append(createElement('span', {
            className: ['icon', item.icon]
        }));
    }

    treeItem.append(createElement('span', {
        className: 'tree-item__title',
        text: item.title
    }));

    const listItem = createElement('li', {
        className: classes,
        children: [treeItem]
    });

    if (treeViewState) {
        treeViewState.registerTreeNode(item, {
            treeItemElement: treeItem.getElement(),
            listItemElement: listItem.getElement(),
            parentItem,
        });
    }

    if (item.children && item.children.length > 0) {
        const nestedList = renderTreeList(item.children, treeViewState, item);
        listItem.append(nestedList);

        if (item.type === 'folder') {
            setFolderOpenedState(listItem.getElement(), item, item.opened);
        }
    }

    treeItem.on('click', (event) => {
        event.stopPropagation();
        const clickedElement = event.currentTarget;

        if (treeViewState) {
            if (item.type === 'folder' && item.children && item.children.length > 0) {
                treeViewState.toggleFolder(item);
            }

            treeViewState.navigateToNode(item, {
                treeItemElement: clickedElement,
                openPath: true,
            });
            return;
        }

        setTreeItemActive(clickedElement);

        if (item.type === 'folder' && item.children && item.children.length > 0) {
            toggleFolder(listItem.getElement(), item);
        }
    });

    return listItem;
}

function renderTreeList(items, treeViewState, parentItem = null) {
    return createElement('ul', {
        className: 'tree-view__list',
        children: items.map((item) => renderTreeItem(item, treeViewState, parentItem))
    });
}

function renderTreeViewList(data = [], workspace = null, treeViewState = null) {
    const treeData = Array.isArray(data)
        ? data
        : [];

    if (workspace && treeViewState) {
        treeViewState.setWorkspace(workspace);
        treeViewState.setTreeData(treeData);
    }

    return renderTreeList(treeData, treeViewState);
}
    return { setTreeItemActive, setFolderOpenedState, renderTreeViewList };
});
