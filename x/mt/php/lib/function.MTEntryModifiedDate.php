<?php
function smarty_function_MTEntryModifiedDate($args, &$ctx) {
    $args['ts'] = $ctx->stash('modification_timestamp');
    return $ctx->_hdlr_date($args, $ctx);
}
?>
