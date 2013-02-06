<?php
function smarty_function_MTCGIPath($args, &$ctx) {
    // status: complete
    // parameters: none
    $path = $ctx->mt->config['CGIPath'];
    if (substr($path, strlen($path) - 1, 1) != '/')
        $path .= '/';
    return $path;
}
?>
