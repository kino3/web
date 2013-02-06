<?php
$_typekeytoken_cache = array();
function smarty_function_MTTypeKeyToken($args, &$ctx) {
    // status: complete
    // parameters: none
    global $_typekeytoken_cache;
    $blog = $ctx->stash('blog');
    $blog_id = $blog['blog_id'];
    if (isset($_typekeytoken_cache[$blog_id])) {
        return $_typekeytoken_cache[$blog_id];
    }
    $blog_token = $blog['blog_remote_auth_token'];
    if ($blog_token) {
        $_typekeytoken_cache[$blog_id] = $blog_token;
        return $blog_token;
    } else {
        # look for authors with permissions for this blog and return
        # the first that has a token
        $auth_token = $ctx->mt->db->get_author_token($blog_id);
        $_typekeytoken_cache[$blog_id] = $auth_token;
        return $auth_token;
    }
}
?>
