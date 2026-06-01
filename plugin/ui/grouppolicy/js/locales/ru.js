define([], function() {
  return {
    // Общие тексты
    common: {
      help: 'Помощь:',
      description: 'Описание:',
      options: 'Опции:',
      comment: 'Комментарий:'
    },

    // Политики
    policies: {
      localGroupPolicy: '[Локальная групповая политика]',
      machine: 'Компьютер',
      machineLevelPolicies: 'Политики настройки компьютера',
      user: 'Пользователь',
      userLevelPolicies: 'Политики настройки пользователей',
      adminTemplates: 'Административные шаблоны',
      machineAdminTemplates: 'Административные шаблоны компьютера',
      localGroupPolicies: 'Шаблон локальных групповых политик',
      policy: 'Политика:',
      policyState: 'Состояние политики:',
      notConfigured: 'Не сконфигурировано',
      enabled: 'Включено',
      disabled: 'Отключено',
      supportedOn: 'Поддерживается на:',
    },

    // Настройки (Preferences)
    preferences: {
      title: 'Настройки',
      description: 'Политики настроек.',
      systemSettings: 'Настройки Системы',
      systemSettingsDesc: 'Политики устанавливающие настройки системы.',
      shortcuts: 'Значки',
      environment: 'Окружение',
      folders: 'Папки',
      registry: 'Реестр',
      driveMaps: 'Сетевые диски',
      networkShares: 'Сетевые папки',
      files: 'Файлы',
      iniFiles: 'Ini файлы'
    },

    treeView: {
      loadingPolicies: 'Loading policies...',
      unableToLoadPolicies: 'Не удалось загрузить политики.'
    },

    header: {
      create: 'Создать',
      edit: 'Изменить',
      delete: 'Удалить',
      apply: 'Применить',
      cancel: 'Отмена',
      information: 'Сведения'
    },

    systemSettings: {
      systemSettings:'Настройки Системы',
      scripts: 'Скрипты'
    },
  };
});
