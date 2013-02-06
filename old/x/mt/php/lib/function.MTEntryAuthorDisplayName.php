<?php
function smarty_function_MTEntryAuthorDisplayName($args, &$ctx) {
    // status: complete
    // parameters: none
    $entry = $ctx->stash('entry');
    $author = $entry['author_nickname'];
    $author or $author = $entry['author_name'];
    return $author;
}
?>
