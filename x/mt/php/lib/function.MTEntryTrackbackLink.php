<?php
function smarty_function_MTEntryTrackbackLink($args, &$ctx) {
    $entry = $ctx->stash('entry');
    if (!$entry) return '';
    if (!$entry['trackback_id']) return '';
    $path = $ctx->mt->config['CGIPath'];
    if (!preg_match('!/$!', $path)) {
        $path .= '/';
    }
    $path .= $ctx->mt->config['TrackbackScript'] . '/' . $entry['trackback_id'];
    return $path;
}
?>
