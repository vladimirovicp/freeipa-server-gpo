define([], function() {

    return {
    // Общие тексты
    common: {
      form: 'Form',
      dialog: 'Dialog',
      help: 'Help:',
      description: 'Description:',
      options: 'Options:',
      edit: 'Edit',
      yes: 'Yes',
      no: 'No',
      name: 'Name',
      path: 'path',
      level: 'level',
      default: 'Default',
      cancel: 'Cancel',
      ok: 'OK',
      open: 'Open',
      save: 'Save',
      delete: 'Delete',
      add: 'Add',
      new: 'New',
      allFiles: 'All files (*.*)',
      fileName: 'File name',
      fileType: 'File type',
      lookIn: 'Look in',
      openFile: 'Open File',
      openDirectory: 'Open Directory',
      information: 'Information message',
      value: 'Value:',
      valueGreaterThanMax: ' is greater than maximum allowed value of:',
      valueLessThanMin: ' is less than minimum allowed value of:',
      maxSet: '. Maximum allowed value has been set.',
      minSet: '. Minimum allowed value has been set.'
    },
  
    // О приложении
    about: {
      title: 'About GPUI',
      copyright: 'Copyright (C) 2022-2023 BaseALT Ltd.',
      version: 'Version '
    },
  
    // Главное окно
    mainWindow: {
      title: 'GPUI',
      search: 'Search...',
      file: '&File',
      view: '&View',
      help: '&Help',
      goBack: 'Go &Back',
      goBackTooltip: 'Go Back',
      goForward: 'Go &Forward',
      goForwardTooltip: 'Go Forward',
      goUp: 'Go &Up',
      goUpTooltip: 'Go Up',
      reload: '&Reload',
      reloadTooltip: 'Reload',
      smallIcons: '&Small Icon View',
      smallIconsTooltip: 'Small Icon View',
      largeIcons: '&Large Icon View',
      largeIconsTooltip: 'Large Icon View',
      compactList: '&Compact List View',
      compactListTooltip: 'Compact List View',
      detailedList: '&Detailed List View',
      detailedListTooltip: 'Detailed List View',
      options: '&Options',
      optionsTooltip: 'Options',
      exit: '&Exit',
      exitTooltip: 'Exit',
      addRemoveColumns: '&Add/Remove Columns',
      addRemoveColumnsTooltip: 'Add/Remove Columns',
      selectDC: '&Select DC',
      selectDomainController: 'Select Domain Controller',
      customize: '&Customize',
      customizeTooltip: 'Customize',
      openPolicyDirectory: 'Open &Policy Directory',
      openUserRegistry: 'Open &User Registry Source',
      saveRegistry: '&Save Registry Source',
      openMachineRegistry: 'Open &Machine Registry Source',
      language: '&Language',
      about: '&About',
      manual: '&Manual',
      shortcuts: {
        altLeft: 'Alt+Left',
        altRight: 'Alt+Right',
        altUp: 'Alt+Up',
        ctrlR: 'Ctrl+R',
        ctrlA: 'Ctrl+A',
        ctrlO: 'Ctrl+O',
        ctrlS: 'Ctrl+S'
      }
    },
  
    // Политики
    policies: {
      domainGroupPolicy: '[Domain Group Policy]',
      localGroupPolicy: '[Local Group Policy]',
      localGroupPolicies: 'Local group policies templates',
      machine: 'Machine',
      machineLevelPolicies: 'Machine level policies',
      user: 'User',
      userLevelPolicies: 'User level policies',
      adminTemplates: 'Administrative Templates',
      machineAdminTemplates: 'Machine administrative templates',
      userAdminTemplates: 'User administrative templates',
      policyState: 'Policy State',
      notConfigured: 'Not Configured',
      enabled: 'Enabled',
      disabled: 'Disabled',
      supportedOn: 'Supported on:'
    },
  
    // Языки
    languages: {
      english: 'English',
      russian: 'Russian'
    },
  
    // Диалоги
    dialogs: {
      listBoxDialog: 'List Dialog',
      saveSettingsTitle: 'Save settings dialog',
      saveSettingsMessage: 'Policy settings were modified do you want to save them?'
    },
  
    // Командная строка
    cli: {
      policyPath: 'The full path of policy to edit.',
      policyBundlePath: 'The full path of policy bundle to load.',
      compatibilityNote: 'This options left for compatibility with ADMC. Currently it does nothing.',
      policyName: 'The name of a policy to display.',
      help: 'Displays help on commandline options.',
      consoleLogLevel: 'Set log level for console.',
      syslogLogLevel: 'Set log level for syslog.',
      fileLogLevel: 'Set log level for file in ~/.local/share/gpui/.',
      badPolicyPath: 'Bad policy path:',
      badLogLevel: 'Bad log level:',
      badPolicyName: 'Bad policy name:'
    },

    // Настройки (Preferences)
    preferences: {
      title: 'Preferences',
      systemSettings: 'System settings',
      environment: 'Environment',
      files: 'Files',
      folders: 'Folders',
      registry: 'Registry',
      networkShares: 'Network Shares',
      driveMaps: 'Drive Maps',
      iniFiles: 'Ini File',
      shortcut: 'Shortcut',
      shortcuts: 'Shortcuts',
    },
  
    // Сообщения
    messages: {
      appliedChanges: 'Applied changes for policy:',
      error: 'Error',
      errorWritingFile: 'Error writing file:',
      errorReadingFile: 'Error reading file:'
    },

  
    // Drives Widget
    drives: {
      form: 'Form',
      hideShowDrive: 'Hide/Show this drive',
      noChange: 'No change',
      hideThisDrive: 'Hide this drive',
      showThisDrive: 'Show this drive',
      hideShowAllDrives: 'Hide/Show all drive',
      hideAllDrives: 'Hide all drive',
      showAllDrives: 'Show all drive',
      action: 'Action:',
      create: 'Create',
      update: 'Update',
      delete: 'Delete',
      reconnect: 'Reconnect:',
      location: 'Location:',
      labelAs: 'Label as:',
      ellipsis: '...',
      driveLetter: 'Drive letter',
      existing: 'Existing:',
      useFirstAvailable: 'Use first available, starting at:'
    },
  
    // Files Widget
    files: {
      form: 'Form',
      action: 'Action:',
      create: 'Create',
      update: 'Update',
      delete: 'Delete',
      sourceFiles: 'Source file(s):',
      placeholder: 'Placeholder',
      ellipsis: '...',
      destination: 'Destination:',
      suppressErrors: 'Supress errors on individual file actions',
      attributes: 'Attributes',
      readOnly: 'Read-only',
      hidden: 'Hidden',
      archive: 'Archive'
    },
  
    // Folders Widget
    folders: {
      form: 'Form',
      action: 'Action:',
      create: 'Create',
      update: 'Update',
      delete: 'Delete',
      path: 'Path:',
      placeholder: 'Placeholder',
      attributes: 'Attributes',
      readOnly: 'Read-only',
      hidden: 'Hidden',
      archive: 'Archive',
      deleteIfEmptied: 'Delete this folder (if emptied)',
      recursivelyDelete: 'Recrusively delete subfolders (if emptied)',
      deleteAllFiles: 'Delete all files in the filder(s)',
      allowReadOnlyDeletion: 'Allow deletion of read-only files/folders',
      ignoreErrors: 'Ignore errors for files/folders cannot be deleted',
      ellipsis: '...'
    },
  
    // INI Widget
    ini: {
      form: 'Form',
      action: 'Action:',
      create: 'Create',
      update: 'Update',
      delete: 'Delete',
      filePath: 'File path',
      sectionName: 'Section Name',
      propertyName: 'Property Name',
      propertyValue: 'Property Value',
      ellipsis: '...'
    },
  
    // Shares Widget
    shares: {
      form: 'Form',
      action: 'Action:',
      create: 'Create',
      update: 'Update',
      delete: 'Delete',
      shareName: 'Share name:',
      folderPath: 'Folder path:',
      comment: 'Comment:',
      ellipsis: '...',
      actionModifiers: 'Action\nModifiers:',
      updateAllRegular: 'Update all regular shares',
      updateAllHidden: 'Update all hidden non-administrative\nshares',
      updateAllAdmin: 'Update all administrative\ndrive-letter shares',
      userLimit: 'User limit:',
      noChange: 'No change',
      maximumAllowed: 'Maximum allowed',
      allowUsers: 'Alow this number of users:',
      accessBasedEnum: 'Access-based\nEnumeration:',
      enable: 'Enable',
      disable: 'Disable'
    },
  
    // Shortcuts Widget
    shortcuts: {
      form: 'Form',
      action: 'Action:',
      create: 'Create',
      replace: 'Replace',
      update: 'Update',
      delete: 'Delete',
      ellipsis: '...',
      targetType: 'Target type:',
      filesystem: 'FILESYSTEM',
      url: 'URL',
      shell: 'SHELL',
      location: 'Location:',
      specifyFullPath: '<Specify full path>',
      desktop: 'Desktop',
      startMenu: 'Start Menu',
      programs: 'Programs',
      startUp: 'StartUp',
      explorerFavorites: 'Explorer Favorites',
      explorerLinks: 'Explorer Links',
      sendTo: 'Send To',
      recent: 'Recent',
      quickLaunch: 'Quick Launch ToolBar',
      myNetworkPlaces: 'My Network Places',
      allUsersDesktop: 'All Users Desktop',
      allUsersStartMenu: 'All Users Start Menu',
      allUsersPrograms: 'All Users Programs',
      allUsersStartUp: 'All Users StartUp',
      allUsersExplorerFavorites: 'All Users Explorer Favorites',
      name: 'Name:',
      targetPath: 'Target path:',
      arguments: 'Arguments:',
      iconFilePath: 'Icon file path:',
      iconIndex: 'Icon index:',
      startIn: 'Start in:',
      shortcutKey: 'Shortcut key:',
      run: 'Run:',
      normalWindow: 'Normal Window',
      minimized: 'Minimized',
      maximized: 'Maximized',
      comment: 'Comment:'
    },
  
    // Variables Widget
    variables: {
      form: 'Form',
      details: 'Details',
      placeholder: 'Placeholder',
      value: 'Value:',
      name: 'Name:',
      or: 'or',
      path: 'PATH',
      partial: 'Partial',
      action: 'Action:',
      create: 'Create',
      update: 'Update',
      delete: 'Delete',
      variableType: 'Variable Type',
      userVariable: 'User Variable',
      systemVariable: 'System Variable'
    },
  
    // Common Widget
    commonWidget: {
      form: 'Form',
      options: 'Options:',
      stopOnError: 'Stop processing items in this extension if an\nerror occurs.',
      runInUserContext: 'Run in logged-on user\'s security\ncontext (user policy option).',
      removeWhenNotApplied: 'Remove this item when it is no longer applied.',
      applyOnce: 'Apply once and do not reapply.',
      itemLevelTargeting: 'Item-level targeting.',
      targeting: 'Targetting...',
      description: 'Description:'
    },
  
    // SMB File Browser
    smb: {
      dialog: 'Dialog',
      back: 'back',
      up: 'Up'
    },
  
  };
});
