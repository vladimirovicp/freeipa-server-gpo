define([], function() {
/**
 * Рекурсивно преобразует узел категории из policy-en.json
 * в формат узла дерева { title, type, opened, icon, children }.
 * @param {Object} categoryNode - узел { category, policies, inherited }
 * @param {Object} ctx - контекст секции/пути
 * @param {string} ctx.sectionClass - 'Machine' | 'User'
 * @param {string[]} ctx.pathSegments - сегменты пути до текущей категории (без её имени)
 * @returns {Object|null} - узел дерева типа folder или null, если категория пуста
 */
function convertPolicyCategory(categoryNode, ctx = {}) {
    const hasInherited = categoryNode.inherited && categoryNode.inherited.length > 0;
    const hasPolicies = categoryNode.policies && Object.keys(categoryNode.policies).length > 0;

    if (!hasInherited && !hasPolicies) {
        return null;
    }

    const sectionClass = ctx.sectionClass || '';
    const baseSegments = Array.isArray(ctx.pathSegments) ? ctx.pathSegments : [];
    const currentCategorySegments = [...baseSegments, categoryNode.category];
    const currentCategoryPath = currentCategorySegments.join('/');

    const children = [];

    if (hasInherited) {
        for (const subCategory of categoryNode.inherited) {
            const converted = convertPolicyCategory(subCategory, {
                sectionClass,
                pathSegments: [...currentCategorySegments, 'inherited'],
            });
            if (converted !== null) {
                children.push(converted);
            }
        }
    }

    if (hasPolicies) {
        for (const [key, policy] of Object.entries(categoryNode.policies)) {
            children.push({
                title: policy.displayName,
                type: 'file',
                icon: 'ico-file',
                policyKey: key,
                policyData: policy,
                template: 'admx',
                admxTreePath: [...currentCategorySegments, 'policies'].join('/'),
            });
        }
    }

    return {
        title: categoryNode.category,
        type: 'folder',
        opened: false,
        icon: 'ico-folder',
        help: categoryNode.help,
        children: children.length > 0 ? children : undefined,
    };
}

/**
 * Преобразует секцию (Machine или User) из policy-en.json
 * в массив корневых узлов дерева.
 * @param {Object} section - объект вида { categories: [...], uncategorizedPolicies: {} }
 * @param {string} sectionClass - 'Machine' | 'User'
 * @returns {Array} - массив узлов дерева
 */
function convertPolicySection(section, sectionClass = '') {
    if (!section || !section.categories) return [];
    return section.categories
        .map((cat) => convertPolicyCategory(cat, {
            sectionClass,
            pathSegments: [sectionClass, 'categories'],
        }))
        .filter(cat => cat !== null);
}
    return { convertPolicySection };
});
