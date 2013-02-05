<?php
function smarty_function_MTStaticWebPath($args, &$ctx) {
    $path = $ctx->mt->config['StaticWebPath'];
    if (!$path) {
        $path = $ctx->mt->config['CGIPath'];
        if (substr($path, strlen($path) - 1, 1) != '/')
            $path .= '/';
        $path .= 'mt-static/';
    }
    if (substr($path, strlen($path) - 1, 1) != '/')
        $path .= '/';
    return $path;
}
?>
