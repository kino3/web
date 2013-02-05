<?php
function smarty_block_MTCategories($args, $content, &$ctx, &$repeat) {
    // status: incomplete
    // parameters: show_empty
    $localvars = array('_categories', '_categories_counter', 'category', 'inside_mt_categories', 'entries');
    if (!isset($content)) {
        $ctx->localize($localvars);
        $args['blog_id'] = $ctx->stash('blog_id');
        $categories = $ctx->mt->db->fetch_categories($args);
        $ctx->stash('_categories', $categories);
        $ctx->stash('inside_mt_categories', 1);
        $counter = 0;
    } else {
        $categories = $ctx->stash('_categories');
        $counter = $ctx->stash('_categories_counter');
    }
    if ($counter < count($categories)) {
        $category = $categories[$counter];
        $ctx->stash('category', $category);
        $ctx->stash('entries', null);
        $ctx->stash('_categories_counter', $counter + 1);
        $repeat = true;
    } else {
        $ctx->restore($localvars);
        $repeat = false;
    }
    return $content;
}
?>
