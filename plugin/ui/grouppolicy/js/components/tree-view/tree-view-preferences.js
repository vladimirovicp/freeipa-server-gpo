define(['../../locales/translations'], function(__dep0) {
var { t } = __dep0;


/** Элементы раздела «Настройки системы» (Компьютер → Настройки → Настройки системы) */
const treepreferences = [
    {
        title: t('preferences.shortcuts'),
        name:'shortcuts',
        type: 'file',
        icon: 'ico-file',
        template: 'preferences',
        header: {
            class: 'Machine'
        }
    },
    {
        title: t('preferences.environment'),
        name:'environment',
        type: 'file',
        icon: 'ico-file',
        template: 'preferences',
        header: {
            class: 'Machine'
        }
    },
    {
        title: t('preferences.folders'),
        name: 'folders',
        type: 'file',
        icon: 'ico-file',
        template: 'preferences',
        header: {
            class: 'Machine'
        }
    },
    {
        title: t('preferences.registry'),
        name: 'registry',
        type: 'file',
        icon: 'ico-file',
        template: 'preferences',
        header: {
            class: 'Machine'
        }
    },
    {
        title: t('preferences.driveMaps'),
        name: 'driveMaps',
        type: 'file',
        icon: 'ico-file',
        template: 'preferences',
        header: {
            class: 'Machine'
        }
    },
    {
        title: t('preferences.networkShares'),
        name: 'networkShares',
        type: 'file',
        icon: 'ico-file',
        template: 'preferences',
        header: {
            class: 'Machine'
        }
    },
    {
        title: t('preferences.files'),
        name: 'files',
        type: 'file',
        icon: 'ico-file',
        template: 'preferences',
        header: {
            class: 'Machine'
        }
    },
    {
        title: t('preferences.iniFiles'),
        name: 'iniFiles',
        type: 'file',
        icon: 'ico-file',
        template: 'preferences',
        header: {
            class: 'Machine'
        }
    }
];
    return { treepreferences };
});
