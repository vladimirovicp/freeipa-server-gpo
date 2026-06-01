define([
    'require',
    'freeipa/ipa',
    'freeipa/phases',
    'freeipa/reg',
    'freeipa/navigation',
    'freeipa/rpc'
], function(require, IPA, phases, reg, navigation, rpc) {

    var exp = IPA.gpo = {};

    (function loadCSS() {
        var files = [
            'js/plugins/chain/css/main.css',
            'js/plugins/chain/css/other.css'
        ];
        files.forEach(function(href) {
            var link = document.createElement('link');
            link.rel = 'stylesheet';
            link.type = 'text/css';
            link.href = href;
            document.head.appendChild(link);
        });
    })();

    var make_gpo_spec = function() {
        return {
            name: 'gpo',
            facet_groups: ['settings'],
            facets: [
                {
                    $type: 'search',
                    name: 'search',
                    label: 'Group Policy Objects',
                    columns: [
                        {
                            name: 'displayname',
                            label: 'Policy Name',
                            primary_key: true
                        },
                        {
                            name: 'cn',
                            label: 'GUID'
                        },
                        {
                            name: 'versionnumber',
                            label: 'Version'
                        },
                        {
                            name: 'flags',
                            label: 'Flags'
                        }
                    ],
                    actions: ['gpui'],
                    control_buttons: [
                        {
                            name: 'gpui',
                            label: 'GPUI',
                            icon: 'fa-external-link'
                        }
                    ]
                },
                {
                    $type: 'details',
                    name: 'details',
                    check_rights: false,
                    actions: ['save', 'revert', 'refresh'],
                    sections: [
                        {
                            name: 'identity',
                            label: 'Identity',
                            fields: [
                                {
                                    name: 'displayname',
                                    label: 'Policy Name',
                                    read_only: false
                                },
                                {
                                    name: 'cn',
                                    label: 'GUID',
                                    read_only: true
                                },
                                {
                                    name: 'distinguishedname',
                                    label: 'Distinguished Name',
                                    read_only: true
                                },
                                {
                                    name: 'gpcfilesyspath',
                                    label: 'File System Path'
                                },
                                {
                                    name: 'versionnumber',
                                    label: 'Version Number'
                                },
                                {
                                    name: 'flags',
                                    label: 'Flags'
                                }
                            ]
                        }
                    ]
                }
            ],
            adder_dialog: {
                title: 'Add Group Policy Object',
                fields: [
                    {
                        name: 'displayname',
                        label: 'Policy Name',
                        required: true
                    }
                ]
            }
        };
    };

    exp.gpo_entity_spec = make_gpo_spec();

    exp.save_action = function(spec) {
        spec = spec || {};
        spec.name = spec.name || 'save';
        spec.label = spec.label || 'Save';
        spec.enable_cond = spec.enable_cond || ['dirty'];
        spec.needs_confirm = spec.needs_confirm !== undefined ? spec.needs_confirm : false;

        var that = IPA.action(spec);

        that.execute_action = function(facet, on_success, on_error) {
            // Get current values from facet
            var values = facet.get_values();
            var original_values = facet.get_original_values();

            // Prepare modification data
            var mod_data = {};
            var has_changes = false;

            // Check ONLY for rename (displayname change)
            // Convert both to strings and trim for comparison
            var current_displayname = String(original_values.displayname || '').trim();
            var new_displayname = String(values.displayname || '').trim();

            // Only rename if name is actually different (not empty, not same)
            if (new_displayname && new_displayname !== current_displayname) {
                mod_data.rename = new_displayname;
                has_changes = true;
            }

            // DO NOT check for changes in other fields
            // Only version will be automatically incremented
            // Other fields remain unchanged unless explicitly renamed
            // Always set has_changes to true to allow version increment
            if (!has_changes) {
                has_changes = true;
            }

            // Check if versionnumber was manually changed
            var version_changed_manually = parseInt(values.versionnumber) !== parseInt(original_values.versionnumber || 0);
            if (version_changed_manually) {
                // Validate manual version change
                var new_version = parseInt(values.versionnumber);
                var current_version = parseInt(original_values.versionnumber || 0);

                if (new_version <= current_version) {
                    IPA.notify('Version number must be greater than current version (' + current_version + '). Auto-incrementing to version ' + (current_version + 1) + '.', 'warning');
                    // Auto-increment instead
                    mod_data.versionnumber = current_version + 1;
                } else {
                    mod_data.versionnumber = new_version;
                    IPA.notify('Using manually specified version: ' + new_version, 'info');
                }
                has_changes = true;
            }

            // If no changes, just return
            if (!has_changes) {
                IPA.notify('No changes made', 'info');
                if (on_success) on_success();
                return;
            }

            // Automatically increment version if there are changes (unless manually changed with valid version)
            if (has_changes && !version_changed_manually) {
                var current_version = parseInt(original_values.versionnumber || 0);
                mod_data.versionnumber = current_version + 1;
            }

            // Get the GPO name (primary key)
            var gpo_name = facet.entity.get_primary_key(original_values);

            // Execute modify command
            var mod_command = rpc.command({
                entity: 'gpo',
                method: 'mod',
                args: [gpo_name],
                options: mod_data,
                on_success: function(mod_result) {
                    facet.refresh();
                    var success_msg = 'GPO "' + gpo_name + '" updated successfully';
                    if (mod_data.rename) {
                        success_msg = 'GPO renamed from "' + gpo_name + '" to "' + mod_data.rename + '" successfully';
                    }
                    // Add version info to success message
                    if (mod_data.versionnumber !== undefined) {
                        success_msg += ' (version: ' + mod_data.versionnumber + ')';
                    }
                    IPA.notify_success(success_msg);
                    if (on_success) on_success(mod_result);
                },
                on_error: function(xhr, text_status, error_thrown) {
                    var msg = 'Failed to update GPO';
                    if (error_thrown && error_thrown.message) {
                        msg += ': ' + error_thrown.message;
                    }
                    IPA.notify(msg, 'error');
                    if (on_error) on_error(xhr, text_status, error_thrown);
                }
            });
            mod_command.execute();
        };

        return that;
    };

        exp.gpui_action = function(spec) {
        spec = spec || {};
        spec.name = spec.name || 'gpui';
        spec.label = spec.label || 'GPUI';
        spec.enable_cond = spec.enable_cond || ['item-selected'];

        var that = IPA.action(spec);

        that.execute_action = function(facet) {
            var selected = facet.get_selected_values();

            if (selected.length !== 1) {
                IPA.notify('Please select exactly one GPO to edit', 'error');
                return;
            }

            var policyName = selected[0];

            var backdrop = $('<div class="modal-backdrop fade in"></div>');
            var modal = $(
                '<div class="modal fade in modal-gpui" style="display:block;" tabindex="-1" role="dialog">' +
                    '<div class="modal-dialog" role="document">' +
                        '<div class="modal-content">' +
                            '<div class="modal-header">' +
                                '<button type="button" class="close" aria-label="Close">' +
                                    '<span aria-hidden="true">&times;</span>' +
                                '</button>' +
                                '<h4 class="modal-title">GPUI | ' + policyName + '</h4>' +
                            '</div>' +
                            '<div class="modal-body">' +
                                '<div id="gp__container" class="gp__container"></div>' +
                            '</div>' +
                        '</div>' +
                    '</div>' +
                '</div>'
            );

            var close_modal = function() {
                modal.remove();
                backdrop.remove();
            };

            modal.find('.close').on('click', close_modal);
            //modal.find('.btn-close-modal').on('click', close_modal);
            backdrop.on('click', close_modal);

            $('body').append(backdrop).append(modal);

            require(['./js/app'], function(app) {
                if (app && typeof app.init === 'function') {
                    app.init({
                        containerId: 'gp__container',
                        policyName: policyName,
                        path: '/'
                    });
                    return;
                }

                IPA.notify('Failed to initialize GPUI module', 'error');
            }, function(err) {
                IPA.notify('Failed to load GPUI module', 'error');
                if (window.console && console.error) {
                    console.error('[gpui] Failed to load app module.', err);
                }
            });
        };

        return that;
    };

    exp.register = function() {
        var e = reg.entity;
        var a = reg.action;

        a.register('save', exp.save_action);
        a.register('gpui', exp.gpui_action);
        e.register({type: 'gpo', spec: exp.gpo_entity_spec});
    };

    phases.on('registration', exp.register);

    return exp;
});
