<?php
function smarty_function_MTRemoteSignOutLink($args, &$ctx) {
    // status: complete
    // parameters: none
    $entry = $ctx->stash('entry');
    $path = $ctx->mt->config['CGIPath'];
    if (!preg_match('!/$!', $path)) {
        $path .= '/';
    }
    return $path . $ctx->mt->config['CommentScript'] .
        '?__mode=handle_sign_in&amp;' .
        ($args['static'] ? 'static=1' : 'static=0') .
        '&amp;entry_id=' . $entry['entry_id'] . '&amp;logout=1';
}
?>
