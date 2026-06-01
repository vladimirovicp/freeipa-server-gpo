define([], function() {

    return {
    // Общие тексты
    common: {
      form: 'Форма',
      dialog: 'Диалог',
      help: 'Помощь:',
      description: 'Описание:',
      options: 'Опции:',
      edit: 'Редактировать',
      yes: 'Да',
      no: 'Нет',
      name: 'Имя',
      path: 'путь',
      level: 'уровень',
      default: 'По умолчанию',
      cancel: 'Отмена',
      ok: 'OK',
      open: 'Открыть',
      save: 'Сохранить',
      delete: 'Удалить',
      add: 'Добавить',
      new: 'Добавить',
      allFiles: 'Все файлы (*.*)',
      fileName: 'Имя файла',
      fileType: 'Тип файлов',
      lookIn: 'Искать в',
      openFile: 'Открыть файл',
      openDirectory: 'Открыть папку',
      information: 'Информация',
      value: 'Значение:',
      valueGreaterThanMax: ' больше максимально возможного значения:',
      valueLessThanMin: ' меньше чем минимально возможное значение:',
      maxSet: '. Максимально возможное значение было установлено.',
      minSet: '. Минимально возможное значение было установлено.'
    },
  
    // О приложении
    about: {
      title: 'О приложении GPUI',
      copyright: 'Авторские права: ООО «Базальт СПО», 2022-2023.',
      version: 'Версия '
    },
  
    // Главное окно
    mainWindow: {
      title: 'GPUI',
      search: 'Поиск...',
      file: 'Файл',
      view: 'Вид',
      help: 'Помощь',
      goBack: 'Назад',
      goForward: 'Вперёд',
      goUp: 'Вверх',
      reload: 'Обновить',
      smallIcons: 'Маленькие иконки',
      largeIcons: 'Большие иконки',
      compactList: 'Компактный список',
      detailedList: 'Детальный список',
      options: 'Настройки',
      exit: 'Выход',
      addRemoveColumns: 'Добавить/Удалить колонки',
      selectDC: 'Выберите контролер домена',
      selectDomainController: 'Выберите контролер домена',
      customize: 'Настроить',
      openPolicyDirectory: 'Открыть папку с ADMX файлами',
      openUserRegistry: 'Открыть пользовательский POL файл',
      saveRegistry: 'Сохранить настройки',
      openMachineRegistry: 'Открыть машинный POL файл',
      language: 'Язык',
      about: 'О приложении',
      manual: 'Руководство',
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
      domainGroupPolicy: '[Доменная групповая политика]',
      localGroupPolicy: '[Локальная групповая политика]',
      localGroupPolicies: 'Шаблон локальных групповых политик',
      machine: 'Компьютер',
      machineLevelPolicies: 'Политики настройки компьютера',
      user: 'Пользователь',
      userLevelPolicies: 'Политики настройки пользователей',
      adminTemplates: 'Административные шаблоны',
      machineAdminTemplates: 'Административные шаблоны компьютера',
      userAdminTemplates: 'Пользовательские административные шаблоны'
    },
  
    // Языки
    languages: {
      english: 'Английский',
      russian: 'Русский'
    },
  
    // Диалоги
    dialogs: {
      listBoxDialog: 'Диалог редактирования списка',
      saveSettingsTitle: 'Состояние настроек',
      saveSettingsMessage: 'Настройки политки были изменены, хотите сохранить их?'
    },
  
    // Командная строка
    cli: {
      policyPath: 'Полный путь для редактируемой политики.',
      policyBundlePath: 'Полный путь к набору ADMX файлов.',
      compatibilityNote: 'Опция оставлена для совместимости с ADMC. Она ничего не делает.',
      policyName: 'Имя политики для отображения.',
      help: 'Показать описание опций коммандной строки.',
      consoleLogLevel: 'Установить уровень логирования для консоли.',
      syslogLogLevel: 'Установить уровень логирования для syslog.',
      fileLogLevel: 'Установить уровень логирования для файла в ~/.local/share/gpui/.',
      badPolicyPath: 'Неверный путь к политике:',
      badLogLevel: 'Неверный уровень логирования:',
      badPolicyName: 'Ошибочное название политики:'
    },

    // Настройки (Preferences)
    preferences: {
      title: 'Настройки',
      description: 'Политики настроек.',
      systemSettings: 'Настройки Системы',
      systemSettingsDesc: 'Политики устанавливающие настройки системы.',
      environment: 'Окружение',
      environmentDesc: 'Настройки переменных окружения.',
      files: 'Файлы',
      filesDesc: 'Политика настройки файлов.',
      folders: 'Папки',
      foldersDesc: 'Политики настройки папок.',
      iniFiles: 'Ini файлы',
      iniFilesDesc: 'Политики настройки Ini файлов.',
      registry: 'Реестр',
      registryDesc: 'Настройки политик реестра.',
      networkShares: 'Сетевые папки',
      networkSharesDesc: 'Настройки сетевых папок.',
      shortcuts: 'Значки',
      shortcutsDesc: 'Настройки значков.',
      driveMaps: 'Сетевые диски',
      driveMapsDesc: 'Настройки сетевых дисков.',
      // Типы политик
      mappedDrive: 'Сетевой диск',
      environmentVariable: 'Переменные окружения',
      file: 'Файл',
      folder: 'Папки',
      iniFile: 'Ini файл',
      registryValue: 'Значение реестра',
      networkShare: 'Сетевая папка',
      shortcut: 'Значок',
      dataSource: 'Источник данных',
      device: 'Устройство',
      localGroup: 'Локальная группа',
      localUser: 'Локальный пользователь',
      vpnConnection: 'VPN Подключение',
      dialUpConnection: 'Dial-Up подключение',
      powerOptions: 'Настройки управления питанием',
      powerScheme: 'Настройки схем питания',
      sharedPrinter: 'Общий принтер',
      tcpipPrinter: 'TCP/IP Принтер',
      localPrinter: 'Локальный принтер',
      folderOptions: 'Настройки папок',
      openWith: 'Открыть с помощью',
      // Действия
      actions: {
        create: 'Создать',
        replace: 'Заменить',
        update: 'Обновить',
        delete: 'Удалить'
      }
    },
  
    // Сообщения
    messages: {
      appliedChanges: 'Применены изменения для политики:'
    }
  };
});
