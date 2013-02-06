<?php
function smarty_block_MTEntriesWithSubCategories($args, $content, &$ctx, &$repeat) {
    $localvars = array('entries');
    if (!isset($content)) {
        if (isset($args['category'])) {
            $kids = $ctx->mt->db->fetch_categories(array('blog_id' => $ctx->stash('blog_id'), 'label' => $args['category']));
        } else {
            $cat = $ctx->stash('category') or
                   $ctx->stash('archive_category');
            if ($cat)
                $kids = array($cat);
        }

        if ($kids) {
            $cats = array();
            while ($c = array_shift($kids)) {
                $cats[] = $c['category_label'];
                $children = $ctx->mt->db->fetch_categories(array('category_id' => $c['category_id'], 'children' => 1));
                if ($children)
                    $kids = array_merge($kids, $children);
            }

            $args['category'] = implode(' OR ', $cats);
            $ctx->localize($localvars);
            $ctx->stash('entries', null);
            require_once("block.MTEntries.php");
        } else {
            $repeat = false;
            return '';
        }
    }
    $output = smarty_block_MTEntries($args, $content, $ctx, $repeat);
    if (!$repeat)
        $ctx->restore($localvars);
    return $output;
}
?>
