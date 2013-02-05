<?php
function smarty_block_MTEntries($args, $content, &$ctx, &$repeat) {
    $localvars = array('entry', '_entries_counter','entries','current_timestamp','modification_timestamp','_entries_lastn', 'current_timestamp_end', 'DateHeader', 'DateFooter', 'EntryBreak');
    if (!isset($content)) {
        $ctx->localize($localvars);
        if (count($args) && ($ctx->stash('entries')))
            $ctx->__stash['entries'] = null;
        $counter = 0;
        $lastn = $args['lastn'];
        $ctx->stash('_entries_lastn', $lastn);
    } else {
        $lastn = $ctx->stash('_entries_lastn');
        $counter = $ctx->stash('_entries_counter');
    }
    $entries = $ctx->stash('entries');
    if (!isset($entries)) {
        $args['blog_id'] = $ctx->stash('blog_id');
        if ($at = $ctx->stash('current_archive_type')) {
            $args['lastn'] or $args['lastn'] = -1;
            $ts = $ctx->stash('current_timestamp');
            $tse = $ctx->stash('current_timestamp_end');
            if (($ts && $tse) && !isset($args['category'])) {
                # only assign a date range if we have both
                # start and end date *and* the user has not
                # explicitly requested a category
                $args['current_timestamp'] = $ts;
                $args['current_timestamp_end'] = $tse;
            }
        }
        if ($cat = $ctx->stash('category')) {
            $args['category'] or $args['category'] = $cat['category_label'];
	}
        $entries = $ctx->mt->db->fetch_entries($args);
        $ctx->stash('entries', $entries);
    }
    if (($lastn > count($entries)) || ($lastn == -1)) {
        $lastn = count($entries);
        $ctx->stash('_entries_lastn', $lastn);
    }
    if ($lastn ? ($counter < $lastn) : ($counter < count($entries))) {
        $entry = $entries[$counter];
        if ($counter > 0) {
            $last_entry_created_on = $entries[$counter-1]['entry_created_on'];
        } else {
            $last_entry_created_on = '';
        }
        if ($counter < count($entries)-1) {
            $next_entry_created_on = $entries[$counter+1]['entry_created_on'];
        } else {
            $next_entry_created_on = '';
        }
        $ctx->stash('DateHeader', !(substr($entry['entry_created_on'], 0, 8) == substr($last_entry_created_on, 0, 8)));
        $ctx->stash('DateFooter', (substr($entry['entry_created_on'], 0, 8) != substr($next_entry_created_on, 0, 8)));
        $ctx->stash('entry', $entry);
        $ctx->stash('current_timestamp', $entry['entry_created_on']);
        $ctx->stash('current_timestamp_end', null);
        $ctx->stash('modification_timestamp', $entry['entry_modified_on']);
        $ctx->stash('_entries_counter', $counter + 1);
        $repeat = true;
    } else {
        $ctx->restore($localvars);
        $repeat = false;
    }
    return $content;
}
?>
