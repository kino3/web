<?php
function smarty_function_MTCategoryTrackbackLink($args, &$ctx) {
    $cat = $ctx->stash('category');
    if (!$cat) return '';
    if (!$cat['trackback_id']) return '';
    $path = $ctx->mt->config['CGIPath'];
    if (!preg_match('!/$!', $path)) {
        $path .= '/';
    }
    $path .= $ctx->mt->config['TrackbackScript'] . '/' . $cat['trackback_id'];
    return $path;
}
?>
