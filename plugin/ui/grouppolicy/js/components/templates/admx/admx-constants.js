define(function() {
const ADMX_DEFAULT_STATE = 'not-configured';
const ADMX_DISABLED_VALUE_MARKER = '**DeleteValues';
const VALID_ADMX_STATES = new Set(['not-configured', 'enabled', 'disabled']);

    return {
        ADMX_DEFAULT_STATE,
        ADMX_DISABLED_VALUE_MARKER,
        VALID_ADMX_STATES,
    };
});
