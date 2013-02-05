<?php
function smarty_block_MTIfCommenterTrusted($args, $content, &$ctx, &$repeat) {
    # status: complete
    if (!isset($content)) {
        $cmtr = $ctx->stash('commenter');
        $trusted = $cmtr['commenter_status'] == 1;
        return $ctx->_hdlr_if($args, $content, $ctx, $repeat, $trusted);
    } else {
        return $ctx->_hdlr_if($args, $content, $ctx, $repeat);
    }
}
?>
