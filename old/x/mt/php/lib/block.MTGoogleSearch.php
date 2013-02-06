<?php
function smarty_block_MTGoogleSearch($args, $content, &$ctx, &$repeat) {
    if (!isset($content)) {
        # required: SOAP/Client package
        require_once("SOAP" . DIRECTORY_SEPARATOR . "Client.php");

        $entry = $ctx->stash('entry');
        $blog = $ctx->stash('blog');

        // Google search query
        if ($args['related']) {
            $related = $args['related'];
        } elseif ($args['title']) {
            $query = $entry['entry_title'];
        } elseif ($args['excerpt']) {
            $query = smarty_function_MTEntryExcerpt(array(), $ctx);
        } elseif ($args['keywords']) {
            $query = $entry['entry_keywords'];
        } else {
            $query = $args['query'];
        }
        $results = $args['results'];

        // Your google license key
        $key = $blog['blog_google_api_key'];

        $s = new SOAP_Client('http://api.google.com/search/beta2');
        $result = $s->call('doGoogleSearch', array(
            'key' => $key,
            'q' => $q,
            'start' => 0,
            'maxResults' => 10,
            'filter' => false,
            'restrict' => '',
            'safeSearch' => false,
            'lr' => '',
            'ie' => '',
            'oe' => '',
        ), 'urn:GoogleSearch');

        // Is result a PEAR_Error?
        if (get_class($result) == 'pear_error') {
            $message = $result->message;
            $output = "An error occured: $message<p>";
        } else {
            // We have proper search results
            $num = $result['estimatedTotalResultsCount'];
            $elements = $result['resultElements'];
            $list = '';
            if ($num > 0) {
                foreach ($elements as $item) {
                        $size = $item['cachedSize'];
                        $title = $item['title'];
                        $url = $item['URL'];
                        $snippet = $item['snippet'];
                        $desc = "<p><b>$title</b> - <a href=\"$url\">$url</a> ";
                        $desc .= "<small>[Size: $size]</small></p>";
                        $desc .= "\n<blockquote>$snippet</blockquote>\n\n";
                        $list .= $desc;
                }
            }
            $output = "$num results returned:\n\n$list";
        }
    }
}
?>
