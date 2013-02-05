<?php
function smarty_function_MTSubCategoryPath($args, &$ctx) {
    require_once("block.MTParentCategories.php");
    require_once("modifier.dirify.php");

    $args = array('glue' => '/');
    $content = null;
    $repeat = true;
    smarty_block_MTParentCategories($args, $content, $ctx, $repeat);
    $res = '';
    while ($repeat) {
        $content = $ctx->tag('MTCategoryLabel');
        $content = smarty_modifier_dirify($content);
        $res .= smarty_block_MTParentCategories($args, $content, $ctx, $repeat);
    }
    return $res;
}
?>
