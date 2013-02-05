<?php
require_once("archive_lib.php");
function smarty_function_MTArchiveTitle($args, &$ctx) {
    $at = $ctx->stash('current_archive_type');
    if (isset($args['archive_type'])) {
        $at = $args['archive_type'];
    }
    if ($at == 'Category') {
        return $ctx->tag('CategoryLabel', $args);
    } elseif ($at == 'Individual') {
        return $ctx->tag('EntryTitle', $args);
    } else {
        # cutting corners here... hope it's sufficient
        # instead of using the date of the entry we have
        # selected, we're going to use the current timestamp
        # available to us for providing the title.
        require_once("block.MTArchiveList.php");
        $sec_title = '_al_'.$at.'_section_title';
        if (function_exists($sec_title)) {
            return $sec_title($args, $ctx);
        } else {
            return $ctx->error("Unsupported archive type: $at");
        }
    }
}
/*
    sub _hdlr_archive_title {
        ## Since this tag can be called from inside <MTCategories>,
        ## we need a way to map this tag to <$MTCategoryLabel$>. 
        return _hdlr_category_label(@_) if $_[0]->{inside_mt_categories};
                                               
        my($ctx) = @_;                            
        my $entries = force($ctx->stash('entries'));
        if (!$entries && (my $e = $ctx->stash('entry'))) {
            push @$entries, $e; 
        }           
        my @entries; 
        my $at = $ctx->{current_archive_type};
        if ($entries && ref($entries) eq 'ARRAY' && $at) {
            @entries = @$entries;
        } else {
            my $blog = $ctx->stash('blog');   
            if (!@entries) {                
            
            ## This situation arises every once in awhile. We have
            ## a date-based archive page, but no entries to go on it--this
            ## might happen, for example, if you have daily archives, and
            ## you post an entry, and then you change the status to draft.
            ## The page will be rebuilt in order to empty it, but in the
            ## process, there won't be any entries in $entries. So, we
            ## build a stub MT::Entry object and set the created_on date
            ## to the current timestamp (start of day/week/month).

                ## But, it's not generally true that draft-izing an entry
                ## erases all of its manifestations. The individual 
                ## archive lingers, for example. --ez
            if ($at && $at =~ /^(Daily|Monthly|Weekly)$/) {
                my $e = MT::Entry->new;
                $e->created_on($ctx->{current_timestamp});
                @entries = ($e);
            } else {

                return $ctx->error(MT->translate(
                    "You used an [_1] tag outside of the proper context.",
                    '<$MTArchiveTitle$>' ));
            }
        }
        }
        if ($ctx->{current_archive_type} eq 'Category') {
            return '' unless @entries;
            return $ctx->stash('archive_category')->label;
        } else {
            my $st= $TypeHandlers{$ctx->{current_archive_type}}{section_title};
            my $title = (@entries && $entries[0]) ? $st->($ctx, $entries[0])
                : $st->($ctx, $ctx->{current_timestamp});
            defined $title ? $title : '';
        }
    }
}
*/
?>
