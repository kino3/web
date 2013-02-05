# Copyright 2001-2005 Six Apart. This code cannot be redistributed without
# permission from www.sixapart.com.  For more information, consult your
# Movable Type license.
#
# $Id: ImportExport.pm 15432 2005-07-29 20:41:11Z bchoate $

package MT::ImportExport;
use strict;

use Symbol;
use MT::Entry;
use MT::Placement;
use MT::Category;
use MT::ErrorHandler;
@MT::ImportExport::ISA = qw( MT::ErrorHandler );

use vars qw( $SEP $SUB_SEP );
$SEP = ('-' x 8);
$SUB_SEP = ('-' x 5);

sub do_import {
    my $class = shift;
    my %param = @_;
    my $stream = $param{Stream} or return $class->error(MT->translate("No Stream"));
    my $blog = $param{Blog} or return $class->error(MT->translate("No Blog"));
    my $cb = $param{Callback} || sub { };

    if (ref($stream) eq 'SCALAR') {
        require IO::String;
        $stream = IO::String->new($$stream);
    } elsif (ref $stream) {
        seek($stream, 0, 0) or return $class->error(MT->translate("Can't rewind"));
    } else {
        my $fh = gensym();
        open $fh, $stream or return $class->error(MT->translate("Can't open '[_1]': [_2]", $stream, $!));
        $stream = $fh;
    }

    require MT::Permission;

    $cb->("Importing entries into blog '", $blog->name, "'\n");

    ## Determine the author as whom we will import the entries.
    my($author, $pass);
    if ($author = $param{ImportAs}) {
        $cb->("Importing entries as author '", $author->name, "'\n");
    } elsif ($author = $param{ParentAuthor}) {
        $pass = $param{NewAuthorPassword}
            or return $class->error(MT->translate(
                "You need to provide a password if you are going to\n" .
                "create new authors for each author listed in your blog.\n"));
        $cb->("Creating new authors for each author found in the blog\n");
    } else {
        return $class->error(MT->translate(
            "Need either ImportAs or ParentAuthor"));
    }
    $cb->("\n");

    my $def_cat_id = $param{DefaultCategoryID};
    my $t_start = $param{TitleStart};
    my $t_end = $param{TitleEnd};
    my $allow_comments = $blog->allow_comments_default;
    my $allow_pings = $blog->allow_pings_default ? 1 : 0;
    my $convert_breaks = $blog->convert_paras;
    my $def_status = $param{DefaultStatus} || $blog->status_default;
    my(%authors, %categories);

    my $blog_id = $blog->id;
    my $author_id = $author->id;

    local $/ = $SEP;
    ENTRY_BLOCK:
    while (<$stream>) {
        my($meta, @pieces) = split /^$SUB_SEP$/m;
        next unless $meta && @pieces;

        ## Create entry object and assign some defaults.
        my $entry = MT::Entry->new;
        $entry->blog_id($blog_id);
        $entry->status($def_status);
        $entry->allow_comments($allow_comments);
        $entry->allow_pings($allow_pings);
        $entry->convert_breaks($convert_breaks);
        $entry->author_id($author->id) if $author;

        ## Some users may want to import just their GM comments, having
        ## already imported their GM entries. We try to match up the
        ## entries using the created on timestamp, and the import file
        ## tells us not to import an entry with the meta-tag "NO ENTRY".
        my $no_save = 0;

        ## Handle all meta-data: author, category, title, date.
        my $i = -1;
        my($primary_cat_id, @placements);
        my @lines = split /\r?\n/, $meta;
        META:
        for my $line (@lines) {
            $i++;
            next unless $line;
            $line =~ s!^\s*!!;
            $line =~ s!\s*$!!;
            my($key, $val) = split /\s*:\s*/, $line, 2;
            if ($key eq 'AUTHOR' && !$author) {
                my $author;
                unless ($author = $authors{$val}) {
                    $author = MT::User->load({ name => $val });
                }
                unless ($author) {
                    $author = MT::User->new;
                    $author->created_by($author_id);
                    $author->name($val);
                    $author->email('');
                    $author->set_password($pass);
                    $cb->("Creating new author ('$val')...");
                    if ($author->save) {
                        $cb->("ok\n");
                    } else {
                        $cb->("failed\n");
                        return $class->error(MT->translate(
                            "Saving author failed: [_1]", $author->errstr));
                    }
                    $authors{$val} = $author;
                    $cb->("Assigning permissions for new author...");
                    my $perms = MT::Permission->new;
                    $perms->blog_id($blog_id);
                    $perms->author_id($author->id);
                    $perms->can_post(1);
                    if ($perms->save) {
                        $cb->("ok\n");
                    } else {
                        $cb->("failed\n");
                        return $class->error(MT->translate(
                         "Saving permission failed: [_1]", $perms->errstr));
                    }
                }
                $entry->author_id($author->id);
            } elsif ($key eq 'CATEGORY' || $key eq 'PRIMARY CATEGORY') {
                if ($val) {
                    my $cat;
                    unless ($cat = $categories{$val}) {
                        $cat = MT::Category->load({ label => $val,
                                                    blog_id => $blog_id });
                    }
                    unless ($cat) {
                        $cat = MT::Category->new;
                        $cat->blog_id($blog_id);
                        $cat->label($val);
                        $cat->author_id($entry->author_id);
                        $cb->("Creating new category ('$val')...");
                        if ($cat->save) {
                            $cb->("ok\n");
                        } else {
                            $cb->("failed\n");
                            return $class->error(MT->translate(
                             "Saving category failed: [_1]", $cat->errstr));
                        }
                        $categories{$val} = $cat;
                    }
                    if ($key eq 'CATEGORY') {
                        push @placements, $cat->id;
                    } else {
                        $primary_cat_id = $cat->id;
                    }
                }
            } elsif ($key eq 'TITLE') {
                $entry->title($val);
            } elsif ($key eq 'DATE') {
                my $dt = MT::Date->parse_date($val);
                $entry->created_on($dt->ts_utc);
            } elsif ($key eq 'STATUS') {
                my $status = MT::Entry::status_int($val)
                    or return $class->error(MT->translate(
                            "Invalid status value '[_1]'", $val));
                $entry->status($status);
            } elsif ($key eq 'ALLOW COMMENTS') {
                $val = 0 unless $val;
                $entry->allow_comments($val);
            } elsif ($key eq 'CONVERT BREAKS') {
                $val = 0 unless $val;
                $entry->convert_breaks($val);
            } elsif ($key eq 'ALLOW PINGS') {
                $val = 0 unless $val;
                return $class->error(MT->translate("Invalid allow pings value '[_1]'", $val))
                    unless $val eq 0 || $val eq 1;
                $entry->allow_pings($val);
            } elsif ($key eq 'NO ENTRY') {
                $no_save++;
            } elsif ($key eq 'START BODY') {
                ## Special case for backwards-compatibility with old
                ## export files: if we see START BODY: on a line, we
                ## gather up the rest of the lines in meta and package
                ## them for handling below in the non-meta area.
                @pieces = ("BODY:\n" . join "\n", @lines[$i+1..$#lines]);
                last META;
            }
        }

        ## If we're not saving this entry (but rather just using it to
        ## import comments, for example), we need to load the relevant
        ## entry using the timestamp.
        if ($no_save) {
            my $ts = $entry->created_on;
            $entry = MT::Entry->load({ created_on => $ts,
                blog_id => $blog_id });
            if (!$entry) {
                $cb->("Can't find existing entry with timestamp " .
                    "'$ts'... skipping comments, and moving on to " .
                    "next entry.\n");
                next ENTRY_BLOCK;
            } else {
                $cb->(sprintf "Importing into existing " .
                    "entry %d ('%s')\n", $entry->id, $entry->title);
            }
        }

        ## Deal with non-meta pieces: entry body, extended entry body,
        ## comments. We need to hold the list of comments until after
        ## we have saved the entry, then assign the new entry ID of
        ## the entry to each comment.
        my(@comments, @pings);
        for my $piece (@pieces) {
            $piece =~ s!^\s*!!;
            $piece =~ s!\s*$!!;
            if ($piece =~ s/^BODY:\s*?\r?\n//) {
                $entry->text($piece);
            }
            elsif ($piece =~ s/^EXTENDED BODY:\s*\r?\n//) {
                $entry->text_more($piece);
            }
            elsif ($piece =~ s/^EXCERPT:\s*\r?\n//) {
                $entry->excerpt($piece) if $piece =~ /\S/;
            }
            elsif ($piece =~ s/^KEYWORDS:\s*\r?\n//) {
                $entry->keywords($piece) if $piece =~ /\S/;
            }
            elsif ($piece =~ s/^COMMENT:\s*\r?\n//) {
                ## Comments are: AUTHOR, EMAIL, URL, IP, DATE (in any order),
                ## then body
                my $comment = MT::Comment->new;
                $comment->blog_id($blog_id);
                my @lines = split /\r?\n/, $piece;
                my($i, $body_idx) = (0) x 2;
                COMMENT:
                for my $line (@lines) {
                    $line =~ s!^\s*!!;
                    my($key, $val) = split /\s*:\s*/, $line, 2;
                    if ($key eq 'AUTHOR') {
                        $comment->author($val);
                    } elsif ($key eq 'EMAIL') {
                        $comment->email($val);
                    } elsif ($key eq 'URL') {
                        $comment->url($val);
                    } elsif ($key eq 'IP') {
                        $comment->ip($val);
                    } elsif ($key eq 'DATE') {
                        my $dt = MT::Date->parse_date($val);
                        $comment->created_on($dt->ts_utc);
                    } else {
                        ## Now we have reached the body of the comment;
                        ## everything from here until the end of the
                        ## array is body.
                        $body_idx = $i;
                        last COMMENT;
                    }
                    $i++;
                }
                $comment->text( join "\n", @lines[$body_idx..$#lines] );
                push @comments, $comment;
            }
            elsif ($piece =~ s/^PING:\s*\r?\n//) {
                ## Pings are: TITLE, URL, IP, DATE, BLOG NAME,
                ## then excerpt
                require MT::TBPing;
                my $ping = MT::TBPing->new;
                $ping->blog_id($blog_id);
                my @lines = split /\r?\n/, $piece;
                my($i, $body_idx) = (0) x 2;
                PING:
                for my $line (@lines) {
                    $line =~ s!^\s*!!;
                    my($key, $val) = split /\s*:\s*/, $line, 2;
                    if ($key eq 'TITLE') {
                        $ping->title($val);
                    } elsif ($key eq 'URL') {
                        $ping->source_url($val);
                    } elsif ($key eq 'IP') {
                        $ping->ip($val);
                    } elsif ($key eq 'DATE') {
                        my $dt = MT::Date->parse_date($val);
                        $ping->created_on($dt->ts_utc);
                    } elsif ($key eq 'BLOG NAME') {
                        $ping->blog_name($val);
                    } else {
                        ## Now we have reached the ping excerpt;
                        ## everything from here until the end of the
                        ## array is body.
                        $body_idx = $i;
                        last PING;
                    }
                    $i++;
                }
                $ping->excerpt( join "\n", @lines[$body_idx..$#lines] );
                push @pings, $ping;
            }
        }

        ## Assign a title if one is not already assigned.
        unless ($entry->title) {
            my $body = $entry->text;
            if ($t_start && $t_end && $body =~
                s!\Q$t_start\E(.*?)\Q$t_end\E\s*!!s) {
                (my $title = $1) =~ s/[\r\n]/ /g;
                $entry->title($title);
                $entry->text($body);
            } else {
                $entry->title( MT::I18N::first_n($body, MT::I18N::const('LENGTH_ENTRY_TITLE_FROM_TEXT')) );
            }
        }

        ## If an entry has comments listed along with it, set
        ## allow_comments to 1 no matter what the default is.
        if (@comments && !$entry->allow_comments) {
            $entry->allow_comments(1);
        }

        ## If an entry has TrackBack pings listed along with it,
        ## set allow_pings to 1 no matter what the default is.
        if (@pings) {
            $entry->allow_pings(1);

            ## If the entry has TrackBack pings, we need to make sure
            ## that an MT::Trackback object is created. To do that, we
            ## need to make sure that $entry->save is called.
            $no_save = 0;
        }

        ## Save entry.
        unless ($no_save) {
            $cb->("Saving entry ('", $entry->title, "')... ");
            if ($entry->save) {
                $cb->("ok (ID ", $entry->id, ")\n");
            } else {
                $cb->("failed\n");
                return $class->error(MT->translate(
                    "Saving entry failed: [_1]", $entry->errstr));
            }
        }

        ## Save placement.
        ## If we have no primary category ID (from a PRIMARY CATEGORY
        ## key), we first look to see if we have any placements from
        ## CATEGORY tags. If so, we grab the first one and use it as the
        ## primary placement. If not, we try to use the default category
        ## ID specified.
        if (!$primary_cat_id) {
            if (@placements) {
                $primary_cat_id = shift @placements;
            } elsif ($def_cat_id) {
                $primary_cat_id = $def_cat_id;
            }
        } else {
            ## If a PRIMARY CATEGORY is also specified as a CATEGORY, we
            ## don't want to add it twice; so we filter it out.
            @placements = grep { $_ != $primary_cat_id } @placements;
        }

        ## So if we have a primary placement from any of the means
        ## specified above, we add the placement.
        if ($primary_cat_id) {
            my $place = MT::Placement->new;
            $place->is_primary(1);
            $place->entry_id($entry->id);
            $place->blog_id($blog_id);
            $place->category_id($primary_cat_id);
            $place->save
                or return $class->error(MT->translate(
                    "Saving placement failed: [_1]", $place->errstr));
        }

        ## Save placements.
        for my $cat_id (@placements) {
            my $place = MT::Placement->new;
            $place->is_primary(0);
            $place->entry_id($entry->id);
            $place->blog_id($blog_id);
            $place->category_id($cat_id);
            $place->save
                or return $class->error(MT->translate(
                    "Saving placement failed: [_1]", $place->errstr));
        }

        ## Save comments.
        for my $comment (@comments) {
            $comment->entry_id($entry->id);
            $cb->("Creating new comment ('", $comment->author, 
                "')... ");
            if ($comment->save) {
                $cb->("ok (ID ", $comment->id, ")\n");
            } else {
                $cb->("failed\n");
                return $class->error(MT->translate(
                    "Saving comment failed: [_1]", $comment->errstr));
            }
        }

        ## Save pings.
        if (@pings) {
            my $tb = MT::Trackback->load({ entry_id => $entry->id })
                or return $class->error(MT->translate(
                    "Entry has no MT::Trackback object!"));
            for my $ping (@pings) {
                $ping->tb_id($tb->id);
                $cb->("Creating new ping ('", $ping->title,
                 "')... ");
                if ($ping->save) {
                    $cb->("ok (ID ", $ping->id, ")\n");
                } else {
                    $cb->("failed\n");
                    return $class->error(MT->translate(
                        "Saving ping failed: [_1]", $ping->errstr));
                }
            }
        }
    }
    1;
}

sub export {
    my $class = shift;
    my($blog, $cb) = @_;
    $cb ||= sub { };

    ## Make sure dates are in English.
    $blog->language('en');

    ## Create template for exporting a single entry
    require MT::Template;
    require MT::Template::Context;
    my $tmpl = MT::Template->new;
    $tmpl->name('Export Template');
    $tmpl->text(<<'TEXT');
AUTHOR: <$MTEntryAuthor strip_linefeeds="1"$>
TITLE: <$MTEntryTitle strip_linefeeds="1"$>
STATUS: <$MTEntryStatus strip_linefeeds="1"$>
ALLOW COMMENTS: <$MTEntryFlag flag="allow_comments"$>
CONVERT BREAKS: <$MTEntryFlag flag="convert_breaks"$>
ALLOW PINGS: <$MTEntryFlag flag="allow_pings"$>
<MTIfNonEmpty tag="MTEntryCategory">PRIMARY CATEGORY: <$MTEntryCategory$>
</MTIfNonEmpty><MTEntryCategories>
CATEGORY: <$MTCategoryLabel$>
</MTEntryCategories>
DATE: <$MTEntryDate format="%m/%d/%Y %I:%M:%S %p"$>
-----
BODY:
<$MTEntryBody convert_breaks="0"$>
-----
EXTENDED BODY:
<$MTEntryMore convert_breaks="0"$>
-----
EXCERPT:
<$MTEntryExcerpt no_generate="1" convert_breaks="0"$>
-----
KEYWORDS:
<$MTEntryKeywords$>
-----
<MTComments>
COMMENT:
AUTHOR: <$MTCommentAuthor strip_linefeeds="1"$>
EMAIL: <$MTCommentEmail strip_linefeeds="1"$>
IP: <$MTCommentIP strip_linefeeds="1"$>
URL: <$MTCommentURL strip_linefeeds="1"$>
DATE: <$MTCommentDate format="%m/%d/%Y %I:%M:%S %p"$>
<$MTCommentBody convert_breaks="0"$>
-----
</MTComments>
<MTPings>
PING:
TITLE: <$MTPingTitle strip_linefeeds="1"$>
URL: <$MTPingURL strip_linefeeds="1"$>
IP: <$MTPingIP strip_linefeeds="1"$>
BLOG NAME: <$MTPingBlogName strip_linefeeds="1"$>
DATE: <$MTPingDate format="%m/%d/%Y %I:%M:%S %p"$>
<$MTPingExcerpt$>
-----
</MTPings>
--------
TEXT

    my $iter = MT::Entry->load_iter({ blog_id => $blog->id },
        { 'sort' => 'created_on', direction => 'ascend' });

    while (my $entry = $iter->()) {
        my $ctx = MT::Template::Context->new;
        $ctx->stash('entry', $entry);
        $ctx->stash('blog', $blog);
        $ctx->stash('blog_id', $blog->id);
	$tmpl->blog_id($blog->id);
        $ctx->{current_timestamp} = $entry->created_on;
        my $res = $tmpl->build($ctx)
            or return $class->error(MT->translate(
                "Export failed on entry '[_1]': [_2]", $entry->title,
                $tmpl->errstr));
        $cb->($res);
    }
    1;
}

1;
