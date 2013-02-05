<?php
function smarty_block_MTEntryIfExtended($args, $content, &$ctx, &$repeat) {
    if (!isset($content)) {
        $entry = $ctx->stash('entry');
        require_once("MTUtil.php");
        return $ctx->_hdlr_if($args, $content, $ctx, $repeat, length_text($entry['entry_text_more']) > 0);
    } else {
        return $ctx->_hdlr_if($args, $content, $ctx, $repeat);
    }
}
?>
