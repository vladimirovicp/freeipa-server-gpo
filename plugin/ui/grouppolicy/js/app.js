define([
    './components/header/header',
    './components/main/main',
    './components/footer/footer',
    './util/resizable',
    './components/templates/default-template',
    './components/templates/scripts-template',
    './components/templates/admx-template',
    './components/templates/folder-template',
    './components/templates/preference/templates-shortcuts',
    './components/templates/preference/templates-environment',
    './components/templates/preference/templates-folders',
    './components/templates/preference/templates-registry',
    './components/templates/preference/templates-driveMaps',
    './components/templates/preference/templates-networkShares',
    './components/templates/preference/templates-files',
    './components/templates/preference/templates-iniFiles',
    './components/tree-view/tree-view-list',
    './util/element-creator',
    './util/mainLocalStorage/shortcuts',
    './locales/translations',
    './util/API'
], function(
    headerModule,
    mainModule,
    footerModule,
    resizableModule,
    defaultTemplateModule,
    scriptsTemplateModule,
    admxTemplateModule,
    folderTemplateModule,
    shortcutsTemplateModule,
    environmentTemplateModule,
    foldersTemplateModule,
    registryTemplateModule,
    driveMapsTemplateModule,
    networkSharesTemplateModule,
    filesTemplateModule,
    iniFilesTemplateModule,
    treeViewListModule,
    elementCreatorModule,
    shortcutsStorageModule,
    translationsModule,
    APIModule
) {
    var renderHeader = headerModule.renderHeader;
    var renderMain = mainModule.renderMain;
    var renderFooter = footerModule.renderFooter;
    var resizable = resizableModule.resizable;
    var renderDefaultTemplate = defaultTemplateModule.renderDefaultTemplate;
    var renderScriptsTemplate = scriptsTemplateModule.renderScriptsTemplate;
    var renderAdmxTemplate = admxTemplateModule.renderAdmxTemplate;
    var renderFolderTemplate = folderTemplateModule.renderFolderTemplate;
    var renderHelpBlock = folderTemplateModule.renderHelpBlock;
    var renderShortcutsTemplate = shortcutsTemplateModule.renderShortcutsTemplate;
    var renderEnvironmentTemplate = environmentTemplateModule.renderEnvironmentTemplate;
    var renderFoldersTemplate = foldersTemplateModule.renderFoldersTemplate;
    var renderRegistryTemplate = registryTemplateModule.renderRegistryTemplate;
    var renderDriveMapsTemplate = driveMapsTemplateModule.renderDriveMapsTemplate;
    var renderNetworkSharesTemplate = networkSharesTemplateModule.renderNetworkSharesTemplate;
    var renderFilesTemplate = filesTemplateModule.renderFilesTemplate;
    var renderIniFilesTemplate = iniFilesTemplateModule.renderIniFilesTemplate;
    var setTreeItemActive = treeViewListModule.setTreeItemActive;
    var setFolderOpenedState = treeViewListModule.setFolderOpenedState;
    var createElement = elementCreatorModule.createElement;
    var initShortcutsStorage = shortcutsStorageModule.initShortcutsStorage;

    function createTreeViewState() {
        return {
            selectedItem: null,
            selectedPath: [],
            workspace: null,
            header: null,
            isHelpOpen: false,
            currentViewCleanup: null,
            renderRequestId: 0,
            treeData: [],
            treeItemElements: new WeakMap(),
            treeListItemElements: new WeakMap(),
            parentItems: new WeakMap(),

            setWorkspace: function(workspace) {
                this.workspace = workspace;
            },

            setTreeData: function(treeData) {
                this.treeData = Array.isArray(treeData)
                    ? treeData
                    : [];
            },

            setHeader: function(header) {
                this.header = header;
            },

            initHelpControls: function() {
                var btnInformation = this.header && this.header.getElement && this.header.getElement()
                    ? this.header.getElement().querySelector('.gp__control-help .btn-information')
                    : null;

                if (!btnInformation) {
                    return;
                }

                btnInformation.addEventListener('click', this.toggleHelp.bind(this));
                this.syncHelpButtonState();
            },

            registerTreeNode: function(item, options) {
                var config = options || {};
                var treeItemElement = config.treeItemElement || null;
                var listItemElement = config.listItemElement || null;
                var parentItem = config.parentItem || null;

                if (!item) {
                    return;
                }

                if (treeItemElement instanceof Element) {
                    this.treeItemElements.set(item, treeItemElement);
                }

                if (listItemElement instanceof Element) {
                    this.treeListItemElements.set(item, listItemElement);
                }

                if (parentItem) {
                    this.parentItems.set(item, parentItem);
                    return;
                }

                this.parentItems.delete(item);
            },

            getPathToItem: function(item) {
                if (!item) {
                    return [];
                }

                var path = [];
                var currentItem = item;

                while (currentItem) {
                    path.unshift(currentItem);
                    currentItem = this.parentItems.get(currentItem) || null;
                }

                return path;
            },

            setFolderOpened: function(item, opened) {
                if (!item || item.type !== 'folder') {
                    return Boolean(item && item.opened);
                }

                var listItemElement = this.treeListItemElements.get(item) || null;
                return setFolderOpenedState(listItemElement, item, opened);
            },

            toggleFolder: function(item) {
                if (!item || item.type !== 'folder' || !Array.isArray(item.children) || item.children.length === 0) {
                    return Boolean(item && item.opened);
                }

                return this.setFolderOpened(item, !item.opened);
            },

            openPathToItem: function(item) {
                var path = this.getPathToItem(item);

                path.slice(0, -1).forEach(function(pathItem) {
                    if (pathItem && pathItem.type === 'folder') {
                        this.setFolderOpened(pathItem, true);
                    }
                }, this);

                return path;
            },

            activateTreeItem: function(item, treeItemElement) {
                var nextTreeItemElement = treeItemElement || this.treeItemElements.get(item) || null;

                if (!nextTreeItemElement) {
                    return null;
                }

                var treeContainer = nextTreeItemElement.closest('.tree-view') || document;
                return setTreeItemActive(nextTreeItemElement, treeContainer);
            },

            cleanupCurrentView: function() {
                if (typeof this.currentViewCleanup === 'function') {
                    this.currentViewCleanup();
                }

                this.currentViewCleanup = null;
            },

            setCurrentView: function(view) {
                this.currentViewCleanup = view && typeof view.cleanup === 'function'
                    ? view.cleanup
                    : null;
            },

            isFolderItemSelected: function() {
                return this.selectedItem && this.selectedItem.item && this.selectedItem.item.type === 'folder';
            },

            isAdmxItemSelected: function() {
                return this.selectedItem
                    && this.selectedItem.item
                    && this.selectedItem.item.type === 'file'
                    && this.selectedItem.item.template === 'admx';
            },

            isHelpToggleAvailable: function() {
                return this.isFolderItemSelected() || this.isAdmxItemSelected();
            },

            getCurrentHelpSourceItem: function() {
                if (this.isFolderItemSelected()) {
                    return this.selectedItem && this.selectedItem.item
                        ? this.selectedItem.item
                        : null;
                }

                return this.selectedPath
                    .slice()
                    .reverse()
                    .find(function(pathItem) {
                        return pathItem && pathItem.type === 'folder';
                    }) || null;
            },

            buildViewWithPersistentHelp: function(view) {
                if (!this.isHelpOpen) {
                    return view;
                }

                var helpSourceItem = this.getCurrentHelpSourceItem();
                var helpBlock = renderHelpBlock({
                    help: helpSourceItem ? helpSourceItem.help : undefined,
                    isOpen: this.isHelpOpen
                });

                if (!helpBlock) {
                    return view;
                }

                return createElement('div', {
                    className: 'gp__list-children-wrapper',
                    children: [view, helpBlock]
                });
            },

            syncHelpButtonState: function() {
                var btnInformation = this.header && this.header.getElement && this.header.getElement()
                    ? this.header.getElement().querySelector('.gp__control-help .btn-information')
                    : null;

                if (!btnInformation) {
                    return;
                }

                btnInformation.classList.toggle('active', this.isHelpToggleAvailable());
            },

            syncHelpBlockState: function() {
                var workspaceEl = this.workspace && this.workspace.getElement
                    ? this.workspace.getElement()
                    : null;
                var helpBlocks = workspaceEl
                    ? workspaceEl.querySelectorAll('.gp__list-children-help, .gp__admx-help')
                    : null;

                if (!helpBlocks || helpBlocks.length === 0) {
                    return;
                }

                helpBlocks.forEach(function(helpBlock) {
                    helpBlock.classList.toggle('is-open', this.isHelpOpen);
                }, this);
            },

            setHelpOpen: function(opened) {
                this.isHelpOpen = Boolean(opened);
                this.syncHelpBlockState();
                return this.isHelpOpen;
            },

            toggleHelp: function() {
                if (!this.isHelpToggleAvailable()) {
                    return this.isHelpOpen;
                }

                return this.setHelpOpen(!this.isHelpOpen);
            },

            renderSelectedItem: async function(item, element) {
                var renderRequestId = ++this.renderRequestId;

                this.cleanupCurrentView();

                if (this.workspace) {
                    this.workspace.clear();
                }

                this.setCurrentView(null);
                this.selectedPath = this.getPathToItem(item);
                this.selectedItem = { item: item, element: element };

                var templateResult = null;
                var renderedWorkspaceView = null;

                if (item && item.type === 'folder') {
                    templateResult = renderFolderTemplate({
                        children: item.children || [],
                        help: item.help,
                        isHelpOpen: this.isHelpOpen,
                        onItemClick: function(childItem) {
                            this.navigateToNode(childItem, {
                                openPath: true,
                                openCurrentFolder: childItem && childItem.type === 'folder' ? true : undefined
                            });
                        }.bind(this)
                    });
                    renderedWorkspaceView = templateResult;
                } else if (item && item.type === 'file') {
                    if (item.template === 'scripts') {
                        if (item.header && item.header.class === 'Machine') {
                            templateResult = renderScriptsTemplate();
                        } else {
                            templateResult = renderDefaultTemplate();
                        }
                    } else if (item.template === 'admx') {
                        templateResult = await renderAdmxTemplate({
                            isHelpOpen: this.isHelpOpen,
                            header: this.header,
                            item: item,
                            admxTreePath: item ? item.admxTreePath : null,
                            isCurrent: function() {
                                return renderRequestId === this.renderRequestId
                                    && this.selectedItem
                                    && this.selectedItem.item === item;
                            }.bind(this)
                        });
                    } else if (item.template !== 'preferences') {
                        templateResult = renderDefaultTemplate();
                    } else if (!item.header || item.header.class !== 'Machine') {
                        templateResult = renderDefaultTemplate();
                    } else {
                        var preferenceTemplateMap = {
                            shortcuts: renderShortcutsTemplate,
                            environment: renderEnvironmentTemplate,
                            folders: renderFoldersTemplate,
                            registry: renderRegistryTemplate,
                            driveMaps: renderDriveMapsTemplate,
                            networkShares: renderNetworkSharesTemplate,
                            files: renderFilesTemplate,
                            iniFiles: renderIniFilesTemplate
                        };

                        var renderTemplate = preferenceTemplateMap[item.name] || renderDefaultTemplate;
                        templateResult = renderTemplate({ header: this.header });
                    }

                    renderedWorkspaceView = templateResult;
                }

                if (renderRequestId !== this.renderRequestId) {
                    if (templateResult && typeof templateResult.cleanup === 'function') {
                        templateResult.cleanup();
                    }
                    return;
                }

                if (this.workspace && renderedWorkspaceView) {
                    this.workspace.append(renderedWorkspaceView);
                    this.setCurrentView(templateResult);
                }

                this.syncHelpButtonState();
                this.syncHelpBlockState();
            },

            navigateToNode: function(item, options) {
                var config = options || {};
                var treeItemElement = config.treeItemElement || null;
                var openPath = config.openPath !== undefined ? config.openPath : true;
                var openCurrentFolder = config.openCurrentFolder;

                if (!item) {
                    return;
                }

                if (openPath) {
                    this.openPathToItem(item);
                }

                if (item.type === 'folder' && openCurrentFolder !== undefined) {
                    this.setFolderOpened(item, openCurrentFolder);
                }

                var activeTreeItemElement = this.activateTreeItem(item, treeItemElement);
                this.renderSelectedItem(item, activeTreeItemElement);
            },

            initializeSelection: function() {
                if (this.selectedItem && this.selectedItem.item) {
                    return;
                }

                var firstRootItem = this.treeData[0] || null;

                if (!firstRootItem) {
                    return;
                }

                this.navigateToNode(firstRootItem, {
                    openPath: true,
                    openCurrentFolder: firstRootItem.type === 'folder' ? true : undefined
                });
            }
        };
    }

    function resolveContainer(options) {
        if (options && options.container instanceof Element) {
            return options.container;
        }

        var containerId = options && options.containerId ? options.containerId : 'gp__container';
        return document.getElementById(containerId);
    }

    function mapBrowserToServiceLocale(browserLang) {
        var lang = (browserLang || 'en').slice(0, 2).toLowerCase();
        if (lang === 'ru') {
            return 'ru-RU';
        }
        return 'en-US';
    }

    function init(options) {
        var container = resolveContainer(options || {});

        if (!container) {
            return null;
        }

        container.innerHTML = '';

        var policyName = (options || {}).policyName;

        APIModule.initNameGpt(policyName).then(function() {
            var browserLang = (navigator.language || 'en').slice(0, 2).toLowerCase();
            var targetLocale = mapBrowserToServiceLocale(browserLang);

            translationsModule.setLanguage(browserLang);

            return APIModule.getLocale().then(function(serviceLocale) {
                if (serviceLocale !== targetLocale) {
                    return APIModule.setLocale(targetLocale);
                }
            });
        }).then(function() {
            initShortcutsStorage();

            var treeViewState = createTreeViewState();
            var header = renderHeader(container);
            treeViewState.setHeader(header);
            treeViewState.initHelpControls();

            var renderedMain = renderMain(container, treeViewState);
            renderFooter(container);

            resizable(
                renderedMain.divider.getElement(),
                renderedMain.treeView.getElement(),
                renderedMain.main.getElement()
            );
        });

        return {
            container: container
        };
    }

    return {
        init: init
    };
});
