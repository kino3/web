<?php
function smarty_function_MTCommenterName($args, &$ctx) {
    $a =& $ctx->stash('commenter');
    isset($a) ? $a['session_name'] : '';
}
?>
