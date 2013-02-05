<?php
function smarty_block_MTIfNonEmpty($args, $content, &$ctx, &$repeat) {
    // status: complete
    // parameters: tag
    if (!isset($content)) {
        $ctx->localize(array('conditional', 'else_content'));
        $tag = $args['tag'];
        $tag = preg_replace('/^MT/', '', $tag);
        $tag = preg_replace('/[^A-Za-z0-9_]/', '', $tag);
        $output = $ctx->tag($tag);
        $ctx->stash('conditional', !empty($output));
        $ctx->stash('else_content', null);
    } else {
        if (!$ctx->stash('conditional')) {
            $content = $ctx->stash('else_content');
        }
        $ctx->restore(array('conditional', 'else_content'));
    }
    return $content;
}
?>
