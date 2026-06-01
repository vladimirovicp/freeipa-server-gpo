define(['../../locales/translations', './tree-view-preferences', './policy-converter', '../../util/API'], function(__dep0, __dep1, __dep2, API) {

var { t } = __dep0;
var { treepreferences } = __dep1;
var { convertPolicySection } = __dep2;


function buildTreeViewList(policyData = {}) {
    const machineCategories = convertPolicySection(policyData.Machine, 'Machine');
    const userCategories = convertPolicySection(policyData.User, 'User');

    return [
        {
            title: t('policies.localGroupPolicy'),
            type: 'folder',
            opened: true,
            icon: null,
            help: t('policies.localGroupPolicies'),
          
            children: [
                {
                    title: t('policies.machine'),
                    type: 'folder',
                    opened: true,
                    icon: 'ico-computer',
                    help: t('policies.machineLevelPolicies'),
                    children: [
                        {
                            title: t('policies.adminTemplates'),
                            type: 'folder',
                            opened: true,
                            icon: 'ico-folder',
                            children: machineCategories,
                            help: t('policies.machineAdminTemplates'),
                        },
                        {
                            title: t('preferences.title'),
                            type: 'folder',
                            opened: false,
                            icon: 'ico-folder',
                            help: t('preferences.description'),
                            children: [
                                {
                                    title: t('preferences.systemSettings'),
                                    type: 'folder',
                                    opened: false,
                                    icon: 'ico-folder',
                                    children: treepreferences,
                                    help: t('preferences.systemSettingsDesc'),
                                }
                            ]
                        },
                        {
                            title: t('preferences.systemSettings'),
                            type: 'folder',
                            opened: false,
                            icon: 'ico-folder',
                            help: t('systemSettings.systemSettings'),
                            children: [
                                {
                                    title: t('systemSettings.scripts'),
                                    type: 'file',
                                    opened: false,
                                    icon: 'ico-file',
                                    template: 'scripts',
                                    header: {
                                        class: 'Machine'
                                    }
                                }
                            ]
                        }
                    ]
                },
                {
                    title: t('policies.user'),
                    type: 'folder',
                    opened: false,
                    icon: 'ico-user',
                    help: t('policies.userLevelPolicies'),
                    children: [
                        {
                            title: t('policies.adminTemplates'),
                            type: 'folder',
                            opened: false,
                            icon: 'ico-folder',
                            children: userCategories
                        },
                        {
                            title: t('preferences.title'),
                            type: 'folder',
                            opened: false,
                            icon: 'ico-folder'
                        },
                        {
                            title: t('preferences.systemSettings'),
                            type: 'folder',
                            opened: false,
                            icon: 'ico-folder',
                            help: t('systemSettings.systemSettings'),
                            children: [
                                {
                                    title: t('systemSettings.scripts'),
                                    type: 'file',
                                    opened: false,
                                    icon: 'ico-file',
                                    template: 'scripts',
                                    header: {
                                        class: 'User'
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ];
}

async function loadTreeViewList() {
    var nameGpt = await API.waitForNameGpt();

    var policyData = await API.getPolicy('/');

    return buildTreeViewList(policyData);
}
    return { loadTreeViewList };
});
