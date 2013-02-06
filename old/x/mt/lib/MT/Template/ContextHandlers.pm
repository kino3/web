# Copyright 2001-2005 Six Apart. This code cannot be redistributed without
# permission from www.sixapart.com.  For more information, consult your
# Movable Type license.
#
# $Id: ContextHandlers.pm 16342 2005-08-17 21:50:11Z ezra $

package MT::Template::Context;
use strict;

use MT::Util qw( start_end_day start_end_week 
		 start_end_month week2ymd munge_comment archive_file_for
                 format_ts offset_time_list first_n_words dirify get_entry
                 encode_html encode_js remove_html wday_from_ts days_in
                 spam_protect encode_php encode_url decode_html encode_xml
                 decode_xml );
use MT::ConfigMgr;
use MT::Request;
use Time::Local qw( timegm );
use MT::ErrorHandler;
use MT::Promise qw(lazy delay force);
use MT::Category;
use MT::Entry;

sub init_default_handlers {
    %MT::Template::Context::Handlers = (
        Else => [ \&_hdlr_pass_tokens, 1 ],
        CGIPath => \&_hdlr_cgi_path,
        AdminCGIPath => \&_hdlr_admin_cgi_path,
        CGIRelativeURL => \&_hdlr_cgi_relative_url,
        CGIHost => \&_hdlr_cgi_host,
        StaticWebPath => \&_hdlr_static_path,
        CommentScript => \&_hdlr_comment_script,
        TrackbackScript => \&_hdlr_trackback_script,
        SearchScript => \&_hdlr_search_script,
        XMLRPCScript => \&_hdlr_xmlrpc_script,
        AtomScript => \&_hdlr_atom_script,
        Date => \&_hdlr_sys_date,
        Version => \&_hdlr_mt_version,
        PublishCharset => \&_hdlr_publish_charset,
        DefaultLanguage => \&_hdlr_default_language,
        CGIServerPath => \&_hdlr_cgi_server_path,
        ConfigFile => \&_hdlr_config_file,

        IfNonEmpty => [ \&_hdlr_if_nonempty, 1 ],
        IfNonZero => [ \&_hdlr_if_nonzero, 1 ],

        CommenterNameThunk => \&_hdlr_commenter_name_thunk,
        CommenterName => \&_hdlr_commenter_name,
        CommenterEmail => \&_hdlr_commenter_email,
        IfCommenterTrusted => [ \&_hdlr_commenter_trusted, 1 ],
        FeedbackScore => \&_hdlr_feedback_score,

        Blogs => [ \&_hdlr_blogs, 1 ],
        BlogID => \&_hdlr_blog_id,
        BlogName => \&_hdlr_blog_name,
        BlogDescription => \&_hdlr_blog_description,
        BlogLanguage => \&_hdlr_blog_language,
        BlogURL => \&_hdlr_blog_url,
        BlogArchiveURL => \&_hdlr_blog_archive_url,
        BlogRelativeURL => \&_hdlr_blog_relative_url,
        BlogSitePath => \&_hdlr_blog_site_path,
        BlogHost => \&_hdlr_blog_host,
        BlogTimezone => \&_hdlr_blog_timezone,
        BlogEntryCount => \&_hdlr_blog_entry_count,
        BlogCommentCount => \&_hdlr_blog_comment_count,
        BlogCCLicenseURL => \&_hdlr_blog_cc_license_url,
        BlogCCLicenseImage => \&_hdlr_blog_cc_license_image,
        CCLicenseRDF => \&_hdlr_cc_license_rdf,
        BlogIfCCLicense => [ \&_hdlr_blog_if_cc_license, 1 ],
        BlogFileExtension => \&_hdlr_blog_file_extension,
        Entries => [ \&_hdlr_entries, 1 ],
        EntriesHeader => [ \&_hdlr_pass_tokens, 1 ],
        EntriesFooter => [ \&_hdlr_pass_tokens, 1 ],
        EntryID => \&_hdlr_entry_id,
        EntryTitle => \&_hdlr_entry_title,
        EntryStatus => \&_hdlr_entry_status,
        EntryFlag => \&_hdlr_entry_flag,
        EntryCategory => \&_hdlr_entry_category,
        EntryCategories => [ \&_hdlr_entry_categories, 1 ],
        EntryBody => \&_hdlr_entry_body,
        EntryMore => \&_hdlr_entry_more,
        EntryExcerpt => \&_hdlr_entry_excerpt,
        EntryKeywords => \&_hdlr_entry_keywords,
        EntryLink => \&_hdlr_entry_link,
        EntryBasename => \&_hdlr_entry_basename,
        EntryAtomID => \&_hdlr_entry_atom_id,
        EntryPermalink => \&_hdlr_entry_permalink,
        EntryAuthor => \&_hdlr_entry_author,
        EntryAuthorDisplayName => \&_hdlr_entry_author_display_name,
        EntryAuthorUsername => \&_hdlr_entry_author_username,
        EntryAuthorEmail => \&_hdlr_entry_author_email,
        EntryAuthorURL => \&_hdlr_entry_author_url,
        EntryAuthorLink => \&_hdlr_entry_author_link,
        EntryAuthorNickname => \&_hdlr_entry_author_nick,
        EntryDate => \&_hdlr_entry_date,
        EntryModifiedDate => \&_hdlr_entry_mod_date,
        EntryCommentCount => \&_hdlr_entry_comments,
        EntryTrackbackCount => \&_hdlr_entry_ping_count,
        BlogIfCommentsOpen => [ \&_hdlr_blog_if_comments_open, 1 ],
        EntryTrackbackLink => \&_hdlr_entry_tb_link,
        EntryTrackbackData => \&_hdlr_entry_tb_data,
        EntryTrackbackID => \&_hdlr_entry_tb_id,
        EntryPrevious => [ \&_hdlr_entry_previous, 1 ],
        EntryNext => [ \&_hdlr_entry_next, 1 ],

        DateHeader => [ \&_hdlr_pass_tokens, 1 ],
        DateFooter => [ \&_hdlr_pass_tokens, 1 ],

        PingsHeader => [ \&_hdlr_pass_tokens, 1 ],
        PingsFooter => [ \&_hdlr_pass_tokens, 1 ],

        ArchivePrevious => [ \&_hdlr_archive_prev_next, 1 ],
        ArchiveNext => [ \&_hdlr_archive_prev_next, 1 ],

        Include => \&_hdlr_include,
        Link => \&_hdlr_link,

        ErrorMessage => \&_hdlr_error_message,

        GetVar => \&_hdlr_var,
        SetVar => \&_hdlr_var,

        IfArchiveTypeEnabled => [ \&_hdlr_archive_type_enabled, 1 ],
        IfCommentsModerated => [ \&_hdlr_comments_moderated, 1 ],
        IfRegistrationRequired => [ \&_hdlr_reg_required, 1 ],
        IfRegistrationNotRequired => [ \&_hdlr_reg_not_required, 1 ],
        IfRegistrationAllowed => [ \&_hdlr_reg_allowed, 1 ],

        IfTypeKeyToken => [ \&_hdlr_if_typekey_token, 1 ],
        TypeKeyToken => \&_hdlr_typekey_token,
        CommentFields => [ \&_hdlr_comment_fields ],
        RemoteSignOutLink => [ \&_hdlr_remote_sign_out_link ],
        RemoteSignInLink => [ \&_hdlr_remote_sign_in_link ],

        Comments => [ \&_hdlr_comments, 1 ],
        CommentsHeader => [ \&_hdlr_pass_tokens, 1 ],
        CommentsFooter => [ \&_hdlr_pass_tokens, 1 ],
        CommentID => \&_hdlr_comment_id,
        CommentEntryID => \&_hdlr_comment_entry_id,
        CommentName => \&_hdlr_comment_author,
        CommentIP => \&_hdlr_comment_ip,
        CommentAuthor => \&_hdlr_comment_author,
        CommentAuthorLink => \&_hdlr_comment_author_link,
        CommentAuthorIdentity => \&_hdlr_comment_author_identity,
        CommentEmail => \&_hdlr_comment_email,
        CommentURL => \&_hdlr_comment_url,
        CommentBody => \&_hdlr_comment_body,
        CommentOrderNumber => \&_hdlr_comment_order_num,
        CommentDate => \&_hdlr_comment_date,
        CommentEntry => [ \&_hdlr_comment_entry, 1 ],
        CommentPreviewAuthor => \&_hdlr_comment_author,
        CommentPreviewIP => \&_hdlr_comment_ip,
        CommentPreviewAuthorLink => \&_hdlr_comment_author_link,
        CommentPreviewEmail => \&_hdlr_comment_email,
        CommentPreviewURL => \&_hdlr_comment_url,
        CommentPreviewBody => \&_hdlr_comment_body,
        CommentPreviewDate => \&_hdlr_date,
        CommentPreviewState => \&_hdlr_comment_prev_state,
        CommentPreviewIsStatic => \&_hdlr_comment_prev_static,

        IndexList => [ \&_hdlr_index_list, 1 ],
        IndexLink => \&_hdlr_index_link,
        IndexName => \&_hdlr_index_name,
        IndexBasename => \&_hdlr_index_basename,

        Archives => [ \&_hdlr_archive_set, 1 ],
        ArchiveList => [ \&_hdlr_archives, 1 ],
        ArchiveListHeader => [ \&_hdlr_pass_tokens, 1 ],
        ArchiveListFooter => [ \&_hdlr_pass_tokens, 1 ],
        ArchiveLink => \&_hdlr_archive_link,
        ArchiveTitle => \&_hdlr_archive_title,
        ArchiveType => \&_hdlr_archive_type,
        ArchiveCount => \&_hdlr_archive_count,
        ArchiveDate => \&_hdlr_date,
        ArchiveDateEnd => \&_hdlr_archive_date_end,
        ArchiveCategory => \&_hdlr_archive_category,
        ArchiveFile => \&_hdlr_archive_file,

        ImageURL => \&_hdlr_image_url,
        ImageWidth => \&_hdlr_image_width,
        ImageHeight => \&_hdlr_image_height,

        Calendar => [ \&_hdlr_calendar, 1 ],
        CalendarDay => \&_hdlr_calendar_day,
        CalendarCellNumber => \&_hdlr_calendar_cell_num,
        CalendarDate => \&_hdlr_date,
        CalendarWeekHeader => [ \&_hdlr_pass_tokens, 1 ],
        CalendarWeekFooter => [ \&_hdlr_pass_tokens, 1 ],
        CalendarIfBlank => [ \&_hdlr_pass_tokens, 1 ],
        CalendarIfToday => [ \&_hdlr_pass_tokens, 1 ],
        CalendarIfEntries => [ \&_hdlr_pass_tokens, 1 ],
        CalendarIfNoEntries => [ \&_hdlr_pass_tokens, 1 ],

        Categories => [ \&_hdlr_categories, 1 ],
        CategoryID => \&_hdlr_category_id,
        CategoryLabel => \&_hdlr_category_label,
        CategoryDescription => \&_hdlr_category_desc,
        CategoryArchiveLink => \&_hdlr_category_archive,
        CategoryCount => \&_hdlr_category_count,
        CategoryTrackbackLink => \&_hdlr_category_tb_link,
        CategoryIfAllowPings => [ \&_hdlr_category_allow_pings, 1 ],
        CategoryTrackbackCount => \&_hdlr_category_tb_count,

        GoogleSearch => [ \&_hdlr_google_search, 1 ],
        GoogleSearchResult => \&_hdlr_google_search_result,

        Pings => [ \&_hdlr_pings, 1 ],
        PingsSent => [ \&_hdlr_pings_sent, 1 ],
        PingsSentURL => \&_hdlr_pings_sent_url,
        PingTitle => \&_hdlr_ping_title,
        PingID => \&_hdlr_ping_id,
        PingURL => \&_hdlr_ping_url,
        PingExcerpt => \&_hdlr_ping_excerpt,
        PingBlogName => \&_hdlr_ping_blog_name,
        PingIP => \&_hdlr_ping_ip,
        PingDate => \&_hdlr_ping_date,

        FileTemplate => \&_hdlr_file_template,

        SignOnURL => \&_hdlr_signon_url,

        IfAllowCommentHTML => [ \&_hdlr_if_allow_comment_html, 1 ],
        IfCommentsAllowed => [ \&_hdlr_if_comments_allowed, 1 ],
        IfCommentsAccepted => [ \&_hdlr_if_comments_accepted, 1 ],
        IfCommentsActive => [ \&_hdlr_if_comments_active, 1 ],
        IfPingsAllowed => [ \&_hdlr_if_pings_allowed, 1 ],
        IfPingsAccepted => [ \&_hdlr_if_pings_accepted, 1 ],
        IfPingsActive => [ \&_hdlr_if_pings_active, 1 ],
        IfDynamicComments => [ \&_hdlr_if_dynamic_comments, 1 ],
        IfDynamicCommentsStaticPage => [ \&_hdlr_if_dynamic_comments, 1 ],
        IfNeedEmail => [ \&_hdlr_if_need_email, 1 ],
        IfRequireCommentEmails => [ \&_hdlr_if_need_email, 1 ],
        #EntryIfAllowComments => [ \&_hdlr_entry_if_allow_comments, 1 ],
        EntryIfAllowComments => [ \&_hdlr_if_comments_active, 1 ],
        EntryIfCommentsOpen => [ \&_hdlr_entry_if_comments_open, 1 ],
        EntryIfAllowPings => [ \&_hdlr_entry_if_allow_pings, 1 ],
        EntryIfExtended => [ \&_hdlr_entry_if_extended, 1 ],

        # Subcategory handlers
        SubCategories => [ \&_hdlr_sub_categories, 1 ],
        SubCatIsFirst => [ \&_hdlr_sub_cat_is_first, 2 ],
        SubCatIsLast => [ \&_hdlr_sub_cat_is_last, 2 ],
        TopLevelCategories => [ \&_hdlr_top_level_categories, 1 ],
        ParentCategory => [ \&_hdlr_parent_category, 1 ],
        ParentCategories => [ \&_hdlr_parent_categories, 1 ],
        TopLevelParent => [ \&_hdlr_top_level_parent, 1 ],
        SubCatsRecurse => \&_hdlr_sub_cats_recurse,
        EntriesWithSubCategories => [ \&_hdlr_entries_with_sub_categories, 1 ],
        SubCategoryPath => \&_hdlr_sub_category_path,
        HasSubCategories => [ \&_hdlr_has_sub_categories, 2 ],
        HasNoSubCategories => [ \&_hdlr_has_no_sub_categories, 2 ],
        HasParentCategory => [ \&_hdlr_has_parent_category, 2 ],
        HasNoParentCategory => [ \&_hdlr_has_no_parent_category, 2 ],
        IfIsAncestor => [ \&_hdlr_is_ancestor, 2 ],
        IfIsDescendant => [ \&_hdlr_is_descendant, 2 ],

        IfStatic => [ sub { 1 }, 2 ],
        IfDynamic => [ sub { 0 }, 2 ],
    );
}

sub _hdlr_if_typekey_token {
    my $blog = $_[0]->stash('blog');
    if ($blog->remote_auth_token) {
        _hdlr_pass_tokens(@_);
    } else {
        _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_comments_moderated {
    my $blog = $_[0]->stash('blog');
    if ($blog->moderate_unreg_comments || $blog->manual_approve_commenters) {
        _hdlr_pass_tokens(@_);
    } else {
        _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_reg_allowed {
    my $blog = $_[0]->stash('blog');
    if ($blog->allow_reg_comments && $blog->effective_remote_auth_token) 
    {
        _hdlr_pass_tokens(@_);
    } else {
        _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_reg_required {
    my $blog = $_[0]->stash('blog');
    if ( $blog->allow_reg_comments && $blog->effective_remote_auth_token
        && ! $blog->allow_unreg_comments ) {
        _hdlr_pass_tokens(@_);
    } else {
        _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_reg_not_required {
    my $blog = $_[0]->stash('blog');
    if ($blog->allow_reg_comments && $blog->effective_remote_auth_token
        && $blog->allow_unreg_comments) {
        _hdlr_pass_tokens(@_);
    } else {
        _hdlr_pass_tokens_else(@_);
    }
}
#FIXME: rethink the above tags.
#  * move all registration conditions into Context.pm?
#  * reg_not_required implies registration is allowed?
#  * moderation includes manual_approve_commenters ??
#  * alias authentication to registration?

sub _hdlr_blog_if_comments_open {
    my $blog = $_[0]->stash('blog');
    if (MT::ConfigMgr->instance->AllowComments &&
        (($blog->allow_reg_comments && $blog->effective_remote_auth_token)
         || $blog->allow_unreg_comments)) {
        _hdlr_pass_tokens(@_);
    } else {
        _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_archive_type_enabled {
    my $blog = $_[0]->stash('blog');
    my @enabled_types = split /,/, $blog->archive_type;
    my $at = $_[1]->{type} || $_[1]->{archive_type};
    if (grep { $_ eq $at } @enabled_types) {
        _hdlr_pass_tokens(@_);
    } else {
        _hdlr_pass_tokens_else(@_);
    }
}

sub sanitize_on {
    $_[0]->{'sanitize'} = 1 unless exists $_[0]->{'sanitize'};
}

sub _hdlr_include {
    my($arg, $cond) = @_[1,2];
    if (my $tmpl_name = $arg->{module}) {
        require MT::Template;
        my $tmpl = MT::Template->load({ name => $tmpl_name,
                                        blog_id => $_[0]->stash('blog_id') })
            or return $_[0]->error(MT->translate(
                "Can't find included template module '[_1]'", $tmpl_name ));
        my $ret = $tmpl->build($_[0], $cond);
        return defined($ret) ? $ret : $_[0]->error($tmpl->errstr);
    } elsif (my $file = $arg->{file}) {
        my $blog = $_[0]->stash('blog');
        my @paths = ($file, map File::Spec->catfile($_, $file),
                            $blog->site_path, $blog->archive_path);
        my $path;
        for my $p (@paths) {
            $path = $p, last if -e $p && -r _;
        }
        return $_[0]->error(MT->translate(
            "Can't find included file '[_1]'", $file )) unless $path;
        local *FH;
        open FH, $path
            or return $_[0]->error(MT->translate(
                "Error opening included file '[_1]': [_2]", $path, $! ));
        my $c = '';
        local $/; $c = <FH>;
        close FH;
        return $c;
    }
}

sub _hdlr_file_template {
    my ($ctx, $args, $cond) = @_;

    my $at = $ctx->{archive_type} || $ctx->{current_archive_type};
    $at = 'Category' if $ctx->{inside_mt_categories};
    my $format = $args->{format};
    unless ($format) {
        my %formats = (
            'Individual' => '%y/%m/%f',
            'Category' => '%c/%f',
            'Monthly' => '%y/%m/%f',
            'Weekly' => '%y/%m/%d-week/%f',
            'Daily' => '%y/%m/%d/%f'
        );
        $format = $formats{ $at };
    }
    return $ctx->error(MT->translate("Unspecified archive template")) unless $format;

    my ($dir, $sep);
    if ($args->{separator}) {
        $dir = "dirify='$args->{separator}'";
        $sep = "separator='$args->{separator}'";
    } else {
        $dir = "dirify='1'";
        $sep = "";
    }
    my %f = (
        'a' => "<MTEntryAuthorNickname $dir>",
        '-a' => "<MTEntryAuthorNickname dirify='-'>",
        '_a' => "<MTEntryAuthorNickname dirify='_'>",
        'b' => "<MTEntryBasename>",
        'c' => "<MTSubCategoryPath $sep>",
        '-c' => "<MTSubCategoryPath separator='-'>",
        '_c' => "<MTSubCategoryPath separator='_'>",
        'C' => "<MTArchiveCategory $dir default=''>",
        '-C' => "<MTArchiveCategory dirify='-' default=''>",
        'd' => "<MTArchiveDate format='%d'>",
        'D' => "<MTArchiveDate format='%e' trim='1'>",
        'e' => "<MTEntryID pad='1'>",
        'E' => "<MTEntryID pad='0'>",
        'f' => "<MTArchiveFile>",
        'F' => "<MTArchiveFile extension='0'>",
        'h' => "<MTArchiveDate format='%H'>",
        'H' => "<MTArchiveDate format='%k' trim='1'>",
        'i' => '<MTIndexBasename extension="1">',
        'I' => "<MTIndexBasename>",
        'j' => "<MTArchiveDate format='%j'>",  # 3-digit day of year
#        'J' => "<MTArchiveDate format=''>",  # day of year
        'm' => "<MTArchiveDate format='%m'>",  # 2-digit month
#        'M' => "<MTArchiveDate format=''>",  # month
        'n' => "<MTArchiveDate format='%M'>",  # 2-digit minute
#        'N' => "<MTArchiveDate format=''>",  # minute
        's' => "<MTArchiveDate format='%S'>",  # 2-digit second
#        'S' => "<MTArchiveDate format=''>",  # second
#        'w' => "<MTArchiveDate format=''>",  # 2-digit week
#        'W' => "<MTArchiveDate format=''>",  # week
        'x' => "<MTBlogFileExtension>",
        'y' => "<MTArchiveDate format='%Y'>",  # year
        'Y' => "<MTArchiveDate format='%y'>",  # 2-digit year
    );
    $format =~ s!%([_-]?[A-Za-z])!$f{$1}!g if defined $format;
    # now build this template and return result
    my $builder = $ctx->stash('builder');
    my $tok = $builder->compile($ctx, $format);
    return $ctx->error(MT->translate("Error in file template: [_1]", $args->{format}))
        unless defined $tok;
    defined(my $file = $builder->build($ctx, $tok, $cond))
        or return $ctx->error($builder->errstr);
    $file =~ s!/{2,}!/!g;
    $file =~ s!(^/|/$)!!g;
    $file;
}

sub _hdlr_link {
    my($ctx, $arg, $cond) = @_;
    my $blog = $ctx->stash('blog');
    if (my $tmpl_name = $arg->{template}) {
        require MT::Template;
        my $tmpl = MT::Template->load({ name => $tmpl_name,
                                        type => 'index',
                                        blog_id => $_[0]->stash('blog_id') })
                || MT::Template->load({ outfile => $tmpl_name,
                                        type => 'index',
                                        blog_id => $_[0]->stash('blog_id') })
            or return $ctx->error(MT->translate(
                "Can't find template '[_1]'", $tmpl_name ));
        my $site_url = $blog->site_url;
        $site_url .= '/' unless $site_url =~ m!/$!;
        my $link = $site_url . $tmpl->outfile;
        $link = MT::Util::strip_index($link, $blog) unless $arg->{with_index};
        $link;
    } elsif (my $entry_id = $arg->{entry_id}) {
        my $entry = MT::Entry->load($entry_id, {cached_ok=>1})
            or return $ctx->error(MT->translate(
                "Can't find entry '[_1]'", $entry_id ));
        my $link = $entry->permalink;
        $link = MT::Util::strip_index($link, $blog) unless $arg->{with_index};
        $link;
    }
}

sub _hdlr_mt_version {
    require MT;
    MT->version_id;
}

sub _hdlr_publish_charset {
    MT::ConfigMgr->instance->PublishCharset || 'iso-8859-1';
}

sub _hdlr_default_language {
    MT::ConfigMgr->instance->DefaultLanguage || 'en';
}

sub _hdlr_signon_url {
    MT::ConfigMgr->instance->get("SignOnURL");
}

sub _hdlr_if_nonempty {
    my ($ctx, $args, $cond) = @_;
    $args->{tag} =~ s/^MT//;
    my $handler = $ctx->handler_for($args->{tag});
    if (defined($handler)) {
	my $value = $handler->($ctx, { %$args });
	if (defined($value) && $value ne '') # want to include "0" here
	{
	    _hdlr_pass_tokens($ctx, $args, $cond);
	} else {
	    _hdlr_pass_tokens_else($ctx, undef, $cond);
	}
    } else {
	_hdlr_pass_tokens_else($ctx);	
    }
}

sub _hdlr_if_nonzero {
    my ($ctx, $args, $cond) = @_;
    $args->{tag} =~ s/^MT//;
    my $handler = $ctx->handler_for($args->{tag});
    if (defined($handler)) {
	my $value = $handler->($ctx, { %$args });
	if (defined($value) && $value)
	{
	    _hdlr_pass_tokens($ctx, $args, $cond);
	} else {
	    _hdlr_pass_tokens_else($ctx, undef, $cond);
	}
    } else {
	_hdlr_pass_tokens_else($ctx);	
    }
}

sub _hdlr_error_message {
    my $err = $_[0]->stash('error_message');
    defined $err ? $err : '';
}

sub _hdlr_var {
    my($ctx, $args) = @_;
    my $tag = $ctx->stash('tag');
    return $ctx->error(MT->translate(
        "You used a [_1] tag without any arguments.", "<MT$tag>" ))
        unless keys %$args && $args->{name};
    if ($tag eq 'SetVar') {
        my $val = defined $args->{value} ? $args->{value} : '';
        $ctx->{__stash}{vars}{$args->{name}} = $val;
    } else {
        return $ctx->{__stash}{vars}{$args->{name}};
    }
    '';
}

sub _hdlr_cgi_path {
    my $path = MT::ConfigMgr->instance->CGIPath;
    $path .= '/' unless $path =~ m!/$!;
    $path;
}
sub _hdlr_admin_cgi_path {
    my $path = MT::ConfigMgr->instance->AdminCGIPath ||
        MT::ConfigMgr->instance->CGIPath;
    $path .= '/' unless $path =~ m!/$!;
    $path;
}
sub _hdlr_config_file {
    MT->instance->{cfg_file};
}
sub _hdlr_cgi_server_path {
    my $path = MT->instance->server_path() || "";
    $path =~ s!/*$!!;
    $path;
}
sub _hdlr_cgi_relative_url {
    my $url = MT::ConfigMgr->instance->CGIPath;
    $url .= '/' unless $url =~ m!/$!;
    if ($url =~ m!^https?://[^/]+(/.*)$!) {
        return $1;
    } else {
        return $url;
    }
}
sub _hdlr_static_path {
    my $path = MT::ConfigMgr->instance->StaticWebPath;
    if (!$path) {
        $path = MT::ConfigMgr->instance->CGIPath;
        $path .= '/' unless $path =~ m!/$!;
        $path .= 'mt-static/';
    }
    $path .= '/' unless $path =~ m!/$!;
    $path;
}
sub _hdlr_comment_script { MT::ConfigMgr->instance->CommentScript }
sub _hdlr_trackback_script { MT::ConfigMgr->instance->TrackbackScript }
sub _hdlr_search_script { MT::ConfigMgr->instance->SearchScript }
sub _hdlr_xmlrpc_script { MT::ConfigMgr->instance->XMLRPCScript }
sub _hdlr_atom_script { MT::ConfigMgr->instance->AtomScript }

sub _hdlr_blogs {
    my($ctx, $args, $cond) = @_;
    my $builder = $ctx->stash('builder');
    my $tokens = $ctx->stash('tokens');
    require MT::Blog;
    my $iter = MT::Blog->load_iter;
    my $res = '';
    while (my $blog = $iter->()) {
        local $ctx->{__stash}{blog} = $blog;
        local $ctx->{__stash}{blog_id} = $blog->id;
        defined(my $out = $builder->build($ctx, $tokens, $cond))
            or return $ctx->error($builder->errstr);
        $res .= $out;
    }
    $res;
}
sub _hdlr_blog_id { $_[0]->stash('blog')->id }
sub _hdlr_blog_name { $_[0]->stash('blog')->name }
sub _hdlr_blog_description {
    my $d = $_[0]->stash('blog')->description;
    defined $d ? $d : '';
}
sub _hdlr_blog_url {
    my $url = $_[0]->stash('blog')->site_url;
    $url .= '/' unless $url =~ m!/$!;
    $url;
}
sub _hdlr_blog_site_path {
    my $path = $_[0]->stash('blog')->site_path;
    $path .= '/' unless $path =~ m!/$!;
    $path;
}
sub _hdlr_blog_archive_url { $_[0]->stash('blog')->archive_url }
sub _hdlr_blog_relative_url {
    my $host = $_[0]->stash('blog')->site_url;
    if ($host =~ m!^https?://[^/]+(/.*)$!) {
        return $1;
    } else {
        return '';
    }
}
sub _hdlr_blog_timezone {
    my $so = $_[0]->stash('blog')->server_offset;
    my $no_colon = $_[1]->{no_colon};
    my $partial_hour_offset = 60 * abs($so - int($so));
    sprintf("%s%02d%s%02d", $so < 0 ? '-' : '+',
	    abs($so), $no_colon ? '' : ':',
	    $partial_hour_offset);
}
{
    my %real_lang = (cz => 'cs', dk => 'da', jp => 'ja', si => 'sl');
sub _hdlr_blog_language {
    my $lang_tag = $_[0]->stash('blog')->language || '';
    $lang_tag = ($real_lang{$lang_tag} || $lang_tag);
    if ($_[1]->{'locale'}) {
        $lang_tag =~ s/^(..)([-_](..))?$/$1 . '_' . uc($3||$1)/e;
    } elsif ($_[1]->{"ietf"}) {
        # http://www.ietf.org/rfc/rfc3066.txt
        $lang_tag =~ s/_/-/;
    }
    $lang_tag;
}
}
sub _hdlr_blog_host {
    my $host = $_[0]->stash('blog')->site_url;
    if ($host =~ m!^https?://([^/:]+)(:\d+)?/!) {
        return $_[1]->{exclude_port} ? $1 : $1 . ($2 || '');
    } else {
        return '';
    }
}
sub _hdlr_cgi_host {
    my $path = _hdlr_cgi_path;
    if ($path =~ m!^https?://([^/:]+)(:\d+)?/!) {
        return $_[1]->{exclude_port} ? $1 : $1 . ($2 || '');
    } else {
        return '';
    }
}
sub _hdlr_blog_entry_count {
    my $blog_id = $_[0]->stash('blog')->id;
    scalar MT::Entry->count({ blog_id => $blog_id,
                              status => MT::Entry::RELEASE() });
}
sub _hdlr_blog_comment_count {
    my $blog_id = $_[0]->stash('blog')->id;
    require MT::Comment;
    scalar MT::Comment->count({ blog_id => $blog_id,
                                visible => 1});
}

sub _hdlr_blog_cc_license_url {
    $_[0]->stash('blog')->cc_license_url;
}
sub _hdlr_blog_cc_license_image {
    my $cc = $_[0]->stash('blog')->cc_license or return;
    my ($code, $license, $image_url) = $cc =~ /(\S+) (\S+) (\S+)/;
    return $image_url if $image_url;
    "http://creativecommons.org/images/public/" .
        ($cc eq 'pd' ? 'norights' : 'somerights');
}
sub _hdlr_cc_license_rdf {
    my($ctx, $arg) = @_;
    my $blog = $ctx->stash('blog');
    my $cc = $blog->cc_license or return;
    my $cc_url = $blog->cc_license_url;
    my $rdf = <<RDF;
<!--
<rdf:RDF xmlns="http://web.resource.org/cc/"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
RDF
    ## SGML comments cannot contain double hyphens, so we convert
    ## any double hyphens to single hyphens.
    my $strip_hyphen = sub {
        (my $s = $_[0]) =~ tr/\-//s;
        $s;
    };
    if (my $entry = $ctx->stash('entry')) {
        my $link = $entry->permalink;
        $link = MT::Util::strip_index($entry->permalink, $blog) unless $arg->{with_index};
        $rdf .= <<RDF;
<Work rdf:about="$link">
<dc:title>@{[ encode_xml($strip_hyphen->($entry->title)) ]}</dc:title>
<dc:description>@{[ encode_xml($strip_hyphen->(_hdlr_entry_excerpt(@_))) ]}</dc:description>
<dc:creator>@{[ encode_xml($strip_hyphen->($entry->author ? $entry->author->name : '')) ]}</dc:creator>
<dc:date>@{[ _hdlr_entry_date($_[0], { 'format' => "%Y-%m-%dT%H:%M:%S" }) .
             _hdlr_blog_timezone($_[0]) ]}</dc:date>
<license rdf:resource="$cc_url" />
</Work>
RDF
    } else {
        $rdf .= <<RDF;
<Work rdf:about="@{[ $blog->site_url ]}">
<dc:title>@{[ encode_xml($strip_hyphen->($blog->name)) ]}</dc:title>
<dc:description>@{[ encode_xml($strip_hyphen->($blog->description)) ]}</dc:description>
<license rdf:resource="$cc_url" />
</Work>
RDF
    }
    $rdf .= MT::Util::cc_rdf($cc) . "</rdf:RDF>\n-->\n";
    $rdf;
}
sub _hdlr_blog_if_cc_license {
    $_[0]->stash('blog')->cc_license ? _hdlr_pass_tokens(@_) : '';
}

sub _hdlr_blog_file_extension {
    my($ctx, $args, $cond) = @_;
    my $blog = $ctx->stash('blog');
    my $ext = $blog->file_extension || '';
    $ext = '.' . $ext if $ext ne '';
    $ext;
}

sub _hdlr_entries {
    my($ctx, $args, $cond) = @_;
    my @entries;
    my $blog_id = $ctx->stash('blog_id');
    my($cat, $author, $saved_entry_stash);
    if ($args->{category}) {
        if (!ref $args->{category} && $args->{category} !~ /\s+(?:AND|OR)\s+/) {
            $cat = cat_path_to_category($args->{category}, $blog_id)
                or return $ctx->error(MT->translate(
                    "No such category '[_1]'", $args->{category}));
        } else {
            my @cat_objs;
            my $is_and;
            if (ref $args->{category}) {
                $is_and = (shift @{$args->{category}}) eq 'AND';
                @cat_objs = @{$args->{category}};
            } elsif (my $cat_name = $args->{category}) {
                $is_and = $cat_name =~ /AND/;
                ## If this is a boolean lookup (like "Foo AND Bar"), we have to
                ## special-case the search. Then we stick the resulting list of
                ## entries into the stash so that it can be filtered using the
                ## mechanism below.
                return $ctx->error(MT->translate(
                                   "You can't use both AND and OR in the same expression ([_1]).",
                                   $cat_name ))
                    if $cat_name =~ /\bAND\b/ && $cat_name =~ /\bOR\b/;
                my @cats = split /\s+(?:AND|OR)\s+/, $cat_name;
                require MT::Placement;
                @cat_objs = map {
                    my $cat = cat_path_to_category($_, $blog_id)
                        # FIXME this won't die to the right place
                        or return $ctx->error(MT->translate(
                                             "No such category '[_1]'", $_ ));
                } @cats;
            }
            my %entries; 
            for my $cat (@cat_objs) {
                my @place = MT::Placement->load({ category_id => $cat->id });
                for my $place (@place) {
                    $entries{$place->entry_id}++;
                }
            }
            my $count = @cat_objs;
            my @ids = $is_and ? grep { $entries{$_} == $count } keys %entries :
                                keys %entries;
            $saved_entry_stash = $ctx->stash('entries') || [];
            if (@$saved_entry_stash) {
                my %temp = map { $_ => 1 } @ids;
                @entries = grep { $temp{$_->id} } @$saved_entry_stash;
            } else {
                for my $entry_id (@ids) {
                    my $entry = MT::Entry->load($entry_id, {cached_ok=>1});
                    push @entries, $entry
                        if $entry->status == MT::Entry::RELEASE();
                }
            }
            $ctx->{__stash}{entries} = \@entries;
            delete $args->{category};
        }
    }
    if (my $author_name = $args->{author}) {
        require MT::Author;
        $author = MT::Author->load({ name => $author_name }) or
            return $ctx->error(MT->translate(
                "No such author '[_1]'", $author_name ));
    }
    my $no_resort = 0;
    my $entries;
    my ($start, $end) = ($ctx->{current_timestamp},
			 $ctx->{current_timestamp_end});

    $entries = force($ctx->stash('entries'));
    if (!($entries && @$entries) && $start && $end) {
 	@entries = MT::Entry->load({blog_id => $blog_id,
				    created_on => [$start, $end]},
				   {range => {created_on => 1}});
	$entries = \@entries;
    }
    if ($entries) {
        @entries = @$entries;
        if (%$args) {
            my $n = $args->{lastn};
            ## If lastn is defined, we need to make sure that the list of
            ## entries is in descending order.
            if ($n) {
                @entries = sort { $b->created_on cmp $a->created_on }
                           @entries;
            }
            my $off = $args->{offset} || 0;
            my($i, $j) = (0, 0);
            my @tmp;
            for my $e (@entries) {
                next if $off && $j++ < $off;
                last if $n && $i >= $n;
                next unless !$cat || $e->is_in_category($cat);
                next unless !$author || $e->author_id == $author->id;
                push @tmp, $e;
                $i++;
            }
            @entries = @tmp;
        }
    } elsif (%$args) {
        my %terms = ( blog_id => $blog_id, status => MT::Entry::RELEASE() );
        $terms{author_id} = $author->id if $author;
        my %args;
        if ($cat) {
            require MT::Placement;
            $args{'join'} = [ 'MT::Placement', 'entry_id',
                              { category_id => $cat->id }, { unique => 1 } ];
        }
        if (my $last = $args->{lastn}) {
            $args{'sort'} = 'created_on';
            $args{direction} = 'descend';
            $args{limit} = $last;
            $args{offset} = $args->{offset} if $args->{offset};
        } elsif (my $days = $args->{days}) {
            my @ago = offset_time_list(time - 3600 * 24 * $days,
                $ctx->stash('blog_id'));
            my $ago = sprintf "%04d%02d%02d%02d%02d%02d",
                $ago[5]+1900, $ago[4]+1, @ago[3,2,1,0];
            $terms{created_on} = [ $ago ];
            %args = ( range => { created_on => 1 } );

        } elsif (my $n = $args->{recently_commented_on}) {
            if (MT::ConfigMgr->instance()->ObjectDriver !~ /postgres/) {
                require MT::Comment;
                $args{'join'} = [ 'MT::Comment', 'entry_id',
                    { blog_id => $blog_id, visible => 1 },
                    { 'sort' => 'created_on',
                      direction => 'descend',
                      unique => 1,
                      limit => $n } ];
                $no_resort = 1;
            } else {
                $args{'join'} = [ 'MT::Comment', 'entry_id',
                                  { blog_id => $blog_id, visible => 1 },
                                  { unique => 1 }];
            }
        }
        @entries = MT::Entry->load(\%terms, \%args);
        if ($args->{recently_commented_on}
            && MT::ConfigMgr->instance()->ObjectDriver =~ /postgres/) {
            my @e = sort {$b->comment_latest->created_on <=> $a->comment_latest->created_on}
                    @entries;
            @entries = splice(@e, 0, $args->{recently_commented_on});
            $no_resort = 1;
        }
    } else {
        if (my $days = $ctx->stash('blog')->days_on_index) {
            my @ago = offset_time_list(time - 3600 * 24 * $days,
                $ctx->stash('blog_id'));
            my $ago = sprintf "%04d%02d%02d%02d%02d%02d",
                $ago[5]+1900, $ago[4]+1, @ago[3,2,1,0];
            @entries = MT::Entry->load({ blog_id => $blog_id,
                                         created_on => [ $ago ],
                                         status => MT::Entry::RELEASE() },
                { range => { created_on => 1 } });
        } elsif (my $limit = $ctx->stash('blog')->entries_on_index) {
            @entries = MT::Entry->load({ blog_id => $blog_id,
                                         status => MT::Entry::RELEASE() },
                { limit => $limit, 'sort' => 'created_on', direction => 'descend' });
        }
    }
    my $res = '';
    my $tok = $ctx->stash('tokens');
    my $builder = $ctx->stash('builder');
    unless ($no_resort) {
        my $so = $args->{sort_order} || $ctx->stash('blog')->sort_order_posts || '';
        my $col = $args->{sort_by} || 'created_on';
        @entries = $so eq 'ascend' ?
            sort { $a->$col() cmp $b->$col() } @entries :
            sort { $b->$col() cmp $a->$col() } @entries;
    }
    my($last_day, $next_day) = ('00000000') x 2;
    my $i = 0;
    for my $e (@entries) {
        local $ctx->{__stash}{entry} = $e;
        local $ctx->{current_timestamp} = $e->created_on;
        local $ctx->{modification_timestamp} = $e->modified_on;
        my $this_day = substr $e->created_on, 0, 8;
        my $next_day = $this_day;
        my $footer = 0;
        if (defined $entries[$i+1]) {
            $next_day = substr($entries[$i+1]->created_on, 0, 8);
            $footer = $this_day ne $next_day;
        } else { $footer++ }
	my $allow_comments ||= 0;
        my $out = $builder->build($ctx, $tok, {
            %$cond,
            DateHeader => ($this_day ne $last_day),
            DateFooter => $footer,
            EntriesHeader => !$i,
            EntriesFooter => !defined $entries[$i+1],
        });
        $last_day = $this_day;
        return $ctx->error( $builder->errstr ) unless defined $out;
        $res .= $out;
        $i++;
    }

    ## Restore a saved entry stash. This is basically emulating "local",
    ## which we can't use, because the local would be buried too far down
    ## in a conditional.
    if ($saved_entry_stash) {
        if (!@$saved_entry_stash) {
            delete $ctx->{__stash}{entries};
        } else {
            $ctx->{__stash}{entries} = $saved_entry_stash;
        }
    }
    $res;
}

sub _no_entry_error {
    return $_[0]->error(MT->translate(
        "You used an '[_1]' tag outside of the context of an entry; perhaps you mistakenly placed it outside of an 'MTEntries' container?",
        $_[1]));
}
sub _hdlr_entry_body {
    my $arg = $_[1];
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryBody');
    my $text = $e->text;
    $text = '' unless defined $text;
    my $convert_breaks = exists $arg->{convert_breaks} ?
        $arg->{convert_breaks} :
            defined $e->convert_breaks ? $e->convert_breaks :
                $_[0]->stash('blog')->convert_paras;
    if ($convert_breaks) {
        my $filters = $e->text_filters;
        push @$filters, '__default__' unless @$filters;
        $text = MT->apply_text_filters($text, $filters, $_[0]);
    }
    return MT::I18N::first_n($text, $arg->{words}) if exists $arg->{words};
    $text;
}
sub _hdlr_entry_more {
    my $arg = $_[1];
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryMore');
    my $text = $e->text_more;
    $text = '' unless defined $text;
    my $convert_breaks = exists $arg->{convert_breaks} ?
        $arg->{convert_breaks} :
            defined $e->convert_breaks ? $e->convert_breaks :
                $_[0]->stash('blog')->convert_paras;
    if ($convert_breaks) {
        my $filters = $e->text_filters;
        push @$filters, '__default__' unless @$filters;
        $text = MT->apply_text_filters($text, $filters, $_[0]);
    }
    $text;
}
sub _hdlr_entry_title {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryTitle');
    my $title = defined $e->title ? $e->title : '';
    $title = MT::I18N::first_n($e->text, MT::I18N::const('LENGTH_ENTRY_TITLE_FROM_TEXT'))
        if !$title && $_[1]->{generate};
    $title;
}
sub _hdlr_entry_status {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryStatus');
    MT::Entry::status_text($e->status);
}
sub _hdlr_entry_date {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryDate');
    my $args = $_[1];
    $args->{ts} = $e->created_on;
    _hdlr_date($_[0], $args);
}
sub _hdlr_entry_mod_date {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryModifiedDate');
    my $args = $_[1];
    $args->{ts} = $e->modified_on;
    _hdlr_date($_[0], $args);
}
sub _hdlr_entry_flag {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryFlag');
    my $flag = $_[1]->{flag}
        or return $_[0]->error(MT->translate(
            'You used <$MTEntryFlag$> without a flag.' ));
    my $v = $e->$flag();
    ## The logic here: when we added the convert_breaks flag, we wanted it
    ## to default to checked, because we added it in 2.0, and people had
    ## previously been using the global convert_paras setting, so we needed
    ## that to be used if it wasn't defined. So that's the reason for the
    ## second test (else) (should we be looking at blog->convert_paras?).
    ## When we added allow_pings, we only want this to be applied if
    ## explicitly checked.
    if ($flag eq 'allow_pings') {
        return defined $v ? $v : 0;
    } else {
        return defined $v ? $v : 1;
    }
}
sub _hdlr_entry_excerpt {
    my($ctx, $args) = @_;
    my $e = $ctx->stash('entry')
        or return $ctx->_no_entry_error('MTEntryExcerpt');
    if (my $excerpt = $e->excerpt) {
        return $excerpt unless $args->{convert_breaks};
        my $filters = $e->text_filters;
        push @$filters, '__default__' unless @$filters;
        return MT->apply_text_filters($excerpt, $filters, $ctx);
    } elsif ($args->{no_generate}) {
        return '';
    }
    my $words = $ctx->stash('blog')->words_in_excerpt;
    $words = 40 unless defined $words && $words ne '';
    my $excerpt = _hdlr_entry_body($ctx, { words => $words, %$args });
    return '' unless $excerpt;
    $excerpt . '...';
}
sub _hdlr_entry_keywords {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryKeywords');
    defined $e->keywords ? $e->keywords : '';
}
sub _hdlr_entry_author {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryAuthor');
    my $a = $e->author;
    $a ? $a->name || '' : '';
}
sub _hdlr_entry_author_display_name {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryAuthorDisplayName');
    my $a = $e->author;
    $a ? $a->nickname || $a->name || '' : '';
}
sub _hdlr_entry_author_nick {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryAuthorNickname');
    my $a = $e->author;
    $a ? $a->nickname || '' : '';
}
sub _hdlr_entry_author_username {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryAuthorUsername');
    my $a = $e->author;
    $a ? $a->name || '' : '';
}
sub _hdlr_entry_author_email {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MT' . $_[0]->stash('tag'));
    my $a = $e->author;
    return '' unless $a && defined $a->email;
    $_[1] && $_[1]->{'spam_protect'} ? spam_protect($a->email) : $a->email;
}
sub _hdlr_entry_author_url {
    my($ctx, $args) = @_;
    my $e = $ctx->stash('entry')
        or return $ctx->_no_entry_error('MT' . $ctx->stash('tag'));
    my $a = $e->author;
    $a ? $a->url || "" : "";
}
sub _hdlr_entry_author_link {
    my($ctx, $args) = @_;
    my $e = $ctx->stash('entry')
        or return $ctx->_no_entry_error('MT' . $ctx->stash('tag'));
    my $a = $e->author;
    return '' unless $a;
    my $name = $a->name || '';
    my $show_email = $args->{show_email} ? 1 : 0;
    my $show_url = 1 unless exists $args->{show_url} && !$args->{show_url};
    if ($show_url && $a->url) {
        return sprintf qq(<a href="%s">%s</a>), $a->url, $name;
    } elsif ($show_email && $a->email) {
        my $str = "mailto:" . $a->email;
        $str = spam_protect($str) if $args->{'spam_protect'};
        return sprintf qq(<a href="%s">%s</a>), $str, $name;
    } else {
        return $name;
    }
}
sub _hdlr_entry_id {
    my $args = $_[1];
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryID');
    $args && $args->{pad} ? (sprintf "%06d", $e->id) : $e->id;
}
sub _hdlr_entry_tb_link {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryTrackbackLink');
    require MT::Trackback;
    my $tb = MT::Trackback->load({ entry_id => $e->id })
        or return '';
    my $cfg = MT::ConfigMgr->instance;
    my $path = $cfg->CGIPath;
    $path .= '/' unless $path =~ m!/$!;
    $path . $cfg->TrackbackScript . '/' . $tb->id;
}
sub _hdlr_entry_tb_data {
    my($ctx, $args) = @_;
    my $e = $ctx->stash('entry')
        or return $ctx->_no_entry_error('MTEntryTrackbackData');
    require MT::Trackback;
    my $tb = MT::Trackback->load({ entry_id => $e->id })
        or return '';
    return '' if $tb->is_disabled;
    my $cfg = MT::ConfigMgr->instance;
    my $path = $cfg->CGIPath;
    $path .= '/' unless $path =~ m!/$!;
    $path .= $cfg->TrackbackScript . '/' . $tb->id;
    my $url;
    if (my $at = $_[0]->{archive_type} || $_[0]->{current_archive_type}) {
        $url = $e->archive_url($at);
        $url .= '#' . sprintf("%06d", $e->id)
            unless $at eq 'Individual';
    } else {
        $url = $e->permalink;
        $url = MT::Util::strip_index($url, $ctx->stash('blog')) unless $args->{with_index};
    }
    my $rdf = '';
    my $comment_wrap = defined $args->{comment_wrap} ?
        $args->{comment_wrap} : 1;
    $rdf .= "<!--\n" if $comment_wrap;
    ## SGML comments cannot contain double hyphens, so we convert
    ## any double hyphens to single hyphens.
    my $strip_hyphen = sub {
        (my $s = $_[0]) =~ tr/\-//s;
        $s;
    };
    $rdf .= <<RDF;
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:trackback="http://madskills.com/public/xml/rss/module/trackback/"
         xmlns:dc="http://purl.org/dc/elements/1.1/">
<rdf:Description
    rdf:about="$url"
    trackback:ping="$path"
    dc:title="@{[ encode_xml($strip_hyphen->($e->title), 1) ]}"
    dc:identifier="$url"
    dc:subject="@{[ encode_xml($e->category ? $e->category->label : '', 1) ]}"
    dc:description="@{[ encode_xml($strip_hyphen->(_hdlr_entry_excerpt(@_)), 1) ]}"
    dc:creator="@{[ encode_xml(_hdlr_entry_author(@_), 1) ]}"
    dc:date="@{[ _hdlr_date($_[0], { 'format' => "%Y-%m-%dT%H:%M:%S" }) .
                 _hdlr_blog_timezone($_[0]) ]}" />
</rdf:RDF>
RDF
    $rdf .= "-->\n" if $comment_wrap;
    $rdf;
}
sub _hdlr_entry_tb_id {
    my($ctx, $args) = @_;
    my $e = $ctx->stash('entry')
        or return $ctx->_no_entry_error('MTEntryTrackbackID');
    require MT::Trackback;
    my $tb = MT::Trackback->load({ entry_id => $e->id })
        or return '';
    $tb->id;
}
sub _hdlr_entry_link {
    my ($ctx, $args) = @_;
    my $e = $ctx->stash('entry')
        or return $ctx->_no_entry_error('MTEntryLink');
    my $blog = $ctx->stash('blog');
    my $arch = $blog->archive_url;
    $arch .= '/' unless $arch =~ m!/$!;

    if (my $at = $args->{archive_type}) {
        my $types = $blog->archive_type;
        return $ctx->error(MT->translate(
            "You used an [_1] tag for linking into '[_2]' archives, but that archive type is not published.", '<$MTEntryLink$>', $at))
            unless $types =~ m/\Q$at\E/;
    }
    my $archive_filename = $e->archive_file($args->{archive_type}
					    ? $args->{archive_type} : ());
    if ($archive_filename) {
        my $link = $arch . $archive_filename;
        $link = MT::Util::strip_index($link, $blog) unless $args->{with_index};
        $link;
    } else { return "" }
}
sub _hdlr_entry_basename {
    my $args = $_[1];
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryBasename');
    return $e->basename();
}
sub _hdlr_entry_atom_id {
    my ($ctx, $args, $cond) = @_;
    my $e = $_[0]->stash('entry')
        or return $ctx->_no_entry_error('MTEntryAtomID');
    return $e->atom_id() || $e->make_atom_id() || $ctx->error(MT->translate("Could not create atom id for entry [_1]", $e->id));
}
sub _hdlr_entry_permalink {
    my ($ctx, $args) = @_;
    my $e = $ctx->stash('entry')
        or return $ctx->_no_entry_error('MTEntryLink');
    my $blog = $ctx->stash('blog');
    if (my $at = $args->{archive_type}) {
        my $types = $blog->archive_type;
        return $ctx->error(MT->translate(
            "You used an [_1] tag for linking into '[_2]' archives, but that archive type is not published.", '<$MTEntryPermalink$>', $at))
            unless $types =~ m/\Q$at\E/;
    }
    my $link = $e->permalink($args ? $args->{archive_type} : undef, 
		  { valid_html => $args->{valid_html} }) or return $ctx->error($e->errstr);
    $link = MT::Util::strip_index($link, $blog) unless $args->{with_index};
    $link;
}
sub _hdlr_entry_category {
    my($ctx, $args, $cond) = @_;
    my $e = $ctx->stash('entry')
        or return $ctx->_no_entry_error('MTEntryCategory');
    my $cat = $e->category;
    return '' unless $cat;
    local $ctx->{__stash}{category} = $e->category;
    &_hdlr_category_label;
}

sub _hdlr_entry_categories {
    my($ctx, $args, $cond) = @_;
    my $e = $ctx->stash('entry')
        or return $ctx->_no_entry_error('MTEntryCategories');
    my $cats = $e->categories;
    return '' unless $cats && @$cats;
    my $builder = $ctx->stash('builder');
    my $tokens = $ctx->stash('tokens');
    my @res;
    for my $cat (@$cats) {
        local $ctx->{__stash}->{category} = $cat;
        defined(my $out = $builder->build($ctx, $tokens, $cond))
            or return $ctx->error( $builder->errstr );
        push @res, $out;
    }
    my $sep = $args->{glue} || '';
    join $sep, @res;
}

sub _hdlr_typekey_token {
    my ($ctx, $args, $cond) = @_;

    my $blog_id = $ctx->stash('blog_id');
    my $blog = MT::Blog->load($blog_id, {cached_ok=>1});
    my $tp_token = $blog->effective_remote_auth_token();
    return $tp_token;
}

sub _hdlr_remote_sign_in_link {
    my ($ctx, $args) = @_;
    my $cfg = MT::ConfigMgr->instance;
    my $blog = $ctx->stash('blog_id');
    $blog = MT::Blog->load($blog, {cached_ok=>1})
        if defined $blog && !(ref $blog);
    my $rem_auth_token = $blog->effective_remote_auth_token();
    return $ctx->error(MT->translate(
                       "To enable comment registration, you need to add a TypeKey token in your weblog config or author profile."))
        unless $rem_auth_token;
    my $needs_email = $blog->require_comment_emails ? "&amp;need_email=1" : "";
    my $signon_url = $cfg->SignOnURL;
    my $path = $cfg->CGIPath;
    $path =~ s|([^/])$|$1/|g;
    my $comment_script = $cfg->CommentScript;
    my $static_arg = $args->{static} ? "static=1" : "static=0";
    my $e = $_[0]->stash('entry');
    my $tk_version = $cfg->TypeKeyVersion ? "&amp;v=" . $cfg->TypeKeyVersion : "";
    my $language = "&amp;lang=" . ($args->{lang} || $cfg->DefaultLanguage || $blog->language);
    return "$signon_url$needs_email$language&amp;t=$rem_auth_token$tk_version&amp;_return=$path$comment_script%3f__mode=handle_sign_in%26$static_arg" .
        ($e ? "%26entry_id=" . $e->id : '');
}

sub _hdlr_remote_sign_out_link {
    my ($ctx, $args) = @_;
    my $cfg = MT::ConfigMgr->instance;
    my $path = $cfg->CGIPath;
    $path =~ s|([^/])$|$1/|g;
    my $comment_script = $cfg->CommentScript;
    my $static_arg = $args->{static} ? "static=1" : "static=0";
    my $e = $_[0]->stash('entry');
    "$path$comment_script?__mode=handle_sign_in&amp;$static_arg&amp;logout=1" .
        ($e ? "&amp;entry_id=" . $e->id : '');
}

sub _hdlr_comment_fields {
    my ($ctx, $args, $cond) = @_;

    my $blog = $ctx->stash('blog_id');
    $blog = MT::Blog->load($blog, {cached_ok=>1}) if defined $blog && !(ref $blog);
    my $cfg = MT::ConfigMgr->instance;

    return '' unless (($blog->allow_reg_comments
                       && $blog->effective_remote_auth_token)
                      || $blog->allow_unreg_comments) && $cfg->AllowComments;

    my $path = $cfg->CGIPath;
    $path =~ s|([^/])$|$1/|g;
    my $comment_script = $cfg->CommentScript;
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryID');
    my $entry_id = $e->id();

    my $signon_url = $cfg->SignOnURL;

    my $allow_comment_html_note = (($blog->allow_comment_html)
				   ? ($args->{html_ok_msg} || 
                                      MT->translate("(You may use HTML tags for style)")) : "");
    my $lang = "&amp;lang=" . ($args->{lang} || $cfg->DefaultLanguage || $blog->language);
    my $needs_email = $blog->require_comment_emails ? "&need_email=1" : "";
    my $registration_required = ($blog->allow_reg_comments
                                 && $blog->effective_remote_auth_token
				 && !$blog->allow_unreg_comments);
    my $registration_allowed = ($blog->allow_reg_comments
                                && $blog->effective_remote_auth_token);
    my $unregistered_allowed = $blog->allow_unreg_comments;

    my $static_arg = $args->{static} ? "static=1" : "static=0";
    my $static_field = ($args->{static} || !defined($args->{static}))
			? (q{<input type="hidden" name="static" value="1" />})
			: (q{<input type="hidden" name="static" value="0" />});

    my $typekey_version = $cfg->TypeKeyVersion;

    my $comment_author = "";
    my $comment_email = "";
    my $comment_text = "";
    my $comment_url = "";
    if ($args->{preview}) {
	local $ctx->{__stash}->{tag} = 'Preview';
        $comment_author = encode_html($ctx->_hdlr_comment_author()) || "";
        $comment_email = encode_html($ctx->_hdlr_comment_email()) || "";
        $comment_text = encode_html($ctx->_hdlr_comment_body({convert_breaks=>0}), 1) || "";
	$comment_url = encode_html($ctx->_hdlr_comment_url()) || "";
    }

    my $rem_auth_token = $blog->effective_remote_auth_token() || "";
    die "To enable comment registration, you need to add a TypeKey token "
	. "in your weblog config or author profile."
	if !$rem_auth_token && $registration_required;
    
    my $tk_version = $cfg->TypeKeyVersion;

    my $javascript = "";

    if ($registration_allowed || $unregistered_allowed) {
        $javascript = <<JAVASCRIPT;
<script type="text/javascript">
function getCookie (name) {
    var prefix = name + \'=\';
    var c = document.cookie;
    var nullstring = \'\';
    var cookieStartIndex = c.indexOf(prefix);
    if (cookieStartIndex == -1)
        return nullstring;
    var cookieEndIndex = c.indexOf(";", cookieStartIndex + prefix.length);
    if (cookieEndIndex == -1)
        cookieEndIndex = c.length;
    return unescape(c.substring(cookieStartIndex + prefix.length, cookieEndIndex));
}
</script>
JAVASCRIPT
    }
    if ($registration_required) {
	return MT->translate_templatized(<<HTML);
$javascript
<div id="thanks">
<p><MT_TRANS phrase="Thanks for signing in,">
<script>document.write(getCookie("commenter_name"))</script>
<MT_TRANS phrase="Now you can comment."> (<a href="$path$comment_script?__mode=handle_sign_in&$static_arg&entry_id=$entry_id&logout=1"><MT_TRANS phrase="sign out"></a>)</p>

<MT_TRANS phrase="(If you haven't left a comment here before, you may need to be approved by the site owner before your comment will appear. Until then, it won't appear on the entry. Thanks for waiting.)">

<form method="post" action="$path$comment_script" name="comments_form" onsubmit="if (this.bakecookie[0].checked) rememberMe(this)">
$static_field
<input type="hidden" name="entry_id" value="$entry_id" />

<p><label for="url">URL:</label><br />
<input tabindex="1" type="text" name="url" id="url" value="$comment_url" />

<MT_TRANS phrase="Remember me?">
<input type="radio" id="remember" name="bakecookie" onclick="rememberMe(this.form)" /><label for="bakecookie"><label for="remember"><MT_TRANS phrase="Yes"></label><input type="radio" id="forget" name="bakecookie" onclick="forgetMe(this.form)" value="Forget Info" style="margin-left: 15px;" /><label for="forget"><MT_TRANS phrase="No"></label><br style="clear: both;" /></p>

<p><label for="text"><MT_TRANS phrase="Comments:"></label><br />
<textarea tabindex="2" id="text" name="text" rows="10" cols="50" id="text">$comment_text</textarea></p>

<div align="center">
<input type="submit" name="preview" value="&nbsp;<MT_TRANS phrase="Preview">&nbsp;" />
<input style="font-weight: bold;" type="submit" name="post" value="&nbsp;<MT_TRANS phrase="Post">&nbsp;" />
</div>

</form>
</div>

<script type="text/javascript">
<!--
if (getCookie("commenter_name")) {
    document.getElementById('thanks').style.display = 'block';
} else {
    document.write('<MT_TRANS phrase="You are not signed in. You need to be registered to comment on this site." escape="singlequotes"> <a href="$signon_url$lang$needs_email&t=$rem_auth_token&v=$tk_version&_return=$path$comment_script%3f__mode=handle_sign_in%26$static_arg%26entry_id=$entry_id"><MT_TRANS phrase="Sign in" escape="singlequotes"></a>');
    document.getElementById('thanks').style.display = 'none';
}
// -->
</script>
<script type="text/javascript">
<!--
if (document.comments_form.email != undefined)
    document.comments_form.email.value = getCookie("mtcmtmail");
if (document.comments_form.author != undefined)
    document.comments_form.author.value = getCookie("mtcmtauth");
if (document.comments_form.url != undefined)
    document.comments_form.url.value = getCookie("mtcmthome");
if (getCookie("mtcmtauth") || getCookie("mtcmthome")) {
    document.comments_form.bakecookie[0].checked = true;
} else {
    document.comments_form.bakecookie[1].checked = true;
}
//-->
</script>
HTML
    ;
    } else {
        my $result = "";
        if ($rem_auth_token && $registration_allowed) {
            $result .= $javascript;
            $result .= MT->translate_templatized(<<HTML);
<script type="text/javascript">
<!--
if (getCookie("commenter_name")) {
    document.write('<MT_TRANS phrase="Thanks for signing in,"> ', getCookie("commenter_name"), '<MT_TRANS phrase=". Now you can comment."> (<a href="$path$comment_script?__mode=handle_sign_in&$static_arg&entry_id=$entry_id&logout=1"><MT_TRANS phrase="sign out"></a>)');
} else {
    document.write('<MT_TRANS phrase="If you have a TypeKey identity, you can " escape="singlequotes"><a href="$signon_url$lang$needs_email&t=$rem_auth_token&v=$tk_version&_return=$path$comment_script%3f__mode=handle_sign_in%26$static_arg%26entry_id=$entry_id"> <MT_TRANS phrase="sign in" escape="singlequotes"></a> <MT_TRANS phrase="to use it here." escape="singlequotes">');
}
// -->
</script>
HTML
        };
        $result .= MT->translate_templatized(<<HTML);
<form method="post" action="$path$comment_script" name="comments_form" onsubmit="if (this.bakecookie[0].checked) rememberMe(this)">
$static_field
<input type="hidden" name="entry_id" value="$entry_id" />

<div id="name_email">
<p><label for="author"><MT_TRANS phrase="Name:"></label><br />
<input tabindex="1" name="author" id="author" value="$comment_author" /></p>

<p><label for="email"><MT_TRANS phrase="Email Address:"></label><br />
<input tabindex="2" name="email" id="email" value="$comment_email" /></p>
</div>
HTML
        if ($rem_auth_token && $registration_allowed) {
	    $result .= MT->translate_templatized(<<HTML)
<script type="text/javascript">
<!--
if (getCookie("commenter_name")) {
    document.getElementById('name_email').style.display = 'none';
}
// -->
</script>
HTML
	}
        $result .= MT->translate_templatized(<<HTML);
<p><label for="url"><MT_TRANS phrase="URL:"></label><br />
<input tabindex="3" type="text" name="url" id="url" value="$comment_url" />

<MT_TRANS phrase="Remember me?">
<input type="radio" id="remember" name="bakecookie" onclick="rememberMe(this.form)" /><label for="remember"><MT_TRANS phrase="Yes"></label><input type="radio" id="forget" name="bakecookie" onclick="forgetMe(this.form)" value="Forget Info" style="margin-left: 15px;" /><label for="forget"><MT_TRANS phrase="No"></label><br style="clear: both;" /></p>

<p><label for="text"><MT_TRANS phrase="Comments:"></label> $allow_comment_html_note<br />
<textarea tabindex="4" name="text" rows="10" cols="50" id="text">$comment_text</textarea></p>

<div align="center">
<input type="submit" name="preview" value="&nbsp;<MT_TRANS phrase="Preview">&nbsp;" />
<input style="font-weight: bold;" type="submit" name="post" value="&nbsp;<MT_TRANS phrase="Post">&nbsp;" />
</div>

</form>

HTML
    if ($args->{preview}) {
        $result .= <<HTML;
<script type="text/javascript" language="javascript">
<!--
if (getCookie("mtcmtauth") || getCookie("mtcmthome")) {
    document.comments_form.bakecookie[0].checked = true;
} else {
    document.comments_form.bakecookie[1].checked = true;
}
//-->
</script>
HTML
    } else {
        $result .= <<HTML;
<script type="text/javascript">
<!--
if (document.comments_form.email != undefined && !document.comments_form.email.value)
    document.comments_form.email.value = getCookie("mtcmtmail");
if (document.comments_form.author != undefined && !document.comments_form.author.value)
    document.comments_form.author.value = getCookie("mtcmtauth");
if (document.comments_form.url != undefined && !document.comments_form.url.value)
    document.comments_form.url.value = getCookie("mtcmthome");
if (getCookie("mtcmtauth") || getCookie("mtcmthome")) {
    document.comments_form.bakecookie[0].checked = true;
} else {
    document.comments_form.bakecookie[1].checked = true;
}
//-->
</script>
HTML
    }
        return $result;
    }
}

sub _hdlr_entry_comments {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryCommentCount');
    $e->comment_count;
}
sub _hdlr_entry_ping_count {
    my $e = $_[0]->stash('entry')
        or return $_[0]->_no_entry_error('MTEntryTrackbackCount');
    $e->ping_count;
}
sub _hdlr_entry_previous {
    my($ctx, $args, $cond) = @_;
    my $e = $ctx->stash('entry')
        or return $ctx->_no_entry_error('MTEntryPrevious');
    my $prev = $e->previous(1);
    my $res = '';
    if ($prev) {
        my $builder = $ctx->stash('builder');
        local $ctx->{__stash}->{entry} = $prev;
        local $ctx->{current_timestamp} = $prev->created_on;
        my $out = $builder->build($ctx, $ctx->stash('tokens'), $cond);
        return $ctx->error( $builder->errstr ) unless defined $out;
        $res .= $out;
    }
    $res;
}
sub _hdlr_entry_next {
    my($ctx, $args, $cond) = @_;
    my $e = $ctx->stash('entry')
        or return $ctx->_no_entry_error('MTEntryNext');
    my $next = $e->next(1);
    my $res = '';
    if ($next) {
        my $builder = $ctx->stash('builder');
        local $ctx->{__stash}->{entry} = $next;
        local $ctx->{current_timestamp} = $next->created_on;
        my $out = $builder->build($ctx, $ctx->stash('tokens'), $cond);
        return $ctx->error( $builder->errstr ) unless defined $out;
        $res .= $out;
    }
    $res;
}

sub _hdlr_pass_tokens {
    my($ctx, $args, $cond) = @_;
    $ctx->stash('builder')->build($ctx, $ctx->stash('tokens'), $cond);
}

sub _hdlr_pass_tokens_else {
    my($ctx, $args, $cond) = @_;
    $ctx->stash('builder')->build($ctx, $ctx->stash('tokens_else'), $cond);
}

sub _hdlr_sys_date {
    my $args = $_[1];
    my $t = time;
    my @ts;
    local $args->{utc};
    if ($args->{utc}) {
        @ts = gmtime $t;
        delete $args->{utc}; # prevents it happening again in _hdlr_date
    } else {
        @ts = offset_time_list($t, $_[0]->stash('blog_id'));
    }
    $args->{ts} = sprintf "%04d%02d%02d%02d%02d%02d",
	$ts[5]+1900, $ts[4]+1, @ts[3,2,1,0];
    _hdlr_date($_[0], $args);
}

sub _hdlr_date {
    my $args = $_[1];
    my $ts = $args->{ts} || $_[0]->{current_timestamp};
    my $tag = $_[0]->stash('tag');
    return $_[0]->error(MT->translate(
        "You used an [_1] tag without a date context set up.", "MT$tag" ))
        unless defined $ts;
    if ($args->{utc}) {
	my $blog = $_[0]->stash('blog');
	$blog = ref $blog ? $blog : MT::Blog->load($blog, {cached_ok=>1});
        my($y, $mo, $d, $h, $m, $s) = $ts =~ /(\d\d\d\d)[^\d]?(\d\d)[^\d]?(\d\d)[^\d]?(\d\d)[^\d]?(\d\d)[^\d]?(\d\d)/;
	my $four_digit_offset = sprintf('%.02d%.02d', int($blog->server_offset),
					60 * abs($blog->server_offset
						 - int($blog->server_offset)));
        require MT::DateTime;
        my $tz_secs = MT::DateTime->tz_offset_as_seconds($four_digit_offset);
        my $ts_utc;
        $mo--;
        if ($] >= 5.006) { # _nocheck is only available with 5.6 and up
            $ts_utc = Time::Local::timegm_nocheck($s, $m, $h, $d, $mo, $y);
        } else {
            $ts_utc = timegm($s, $m, $h, $d, $mo, $y - 1900);
        }
        $ts_utc -= $tz_secs;
        ($s, $m, $h, $d, $mo, $y) = gmtime( $ts_utc );
        $y += 1900; $mo++;
        $ts = sprintf("%04d%02d%02d%02d%02d%02d", $y, $mo, $d, $h, $m, $s);
    }
    if (my $format = $args->{format_name}) {
        if ($format eq 'rfc822') {
	    my $blog = $_[0]->stash('blog');
	    $blog = ref $blog ? $blog : MT::Blog->load($blog, {cached_ok=>1});
            my $so = $blog->server_offset;
            my $partial_hour_offset = 60 * abs($so - int($so));
            my $tz = sprintf("%s%02d%02d", $so < 0 ? '-' : '+',
	        abs($so), $partial_hour_offset);
            ## RFC-822 dates must be in English.
            $args->{'format'} = '%a, %d %b %Y %H:%M:%S ' . $tz;
            $args->{language} = 'en';
        }
    }
    format_ts($args->{'format'}, $ts, $_[0]->stash('blog'), $args->{language});
}

sub _no_comment_error {
    return $_[0]->error(MT->translate(
        "You used an '[_1]' tag outside of the context of a comment; perhaps you mistakenly placed it outside of an 'MTComments' container?",
        $_[1] ));
}
sub _hdlr_comments {
    my($ctx, $args, $cond) = @_;
    my $blog_id = $ctx->stash('blog_id');
    my @comments;
    my $so = $args->{sort_order} || $ctx->stash('blog')->sort_order_comments;
    ## If there is a "lastn" arg, then we need to check if there is an entry
    ## in context. If so, grab the N most recent comments for that entry;
    ## otherwise, grab the N most recent comments for the entire blog.
    if (my $n = $args->{lastn}) {
        if (my $e = $ctx->stash('entry')) {
            ## Sort in descending order, then grab the first $n ($n most
            ## recent) comments.
            my $comments = $e->comments;
            @comments = $so eq 'ascend' ?
                sort { $a->created_on <=> $b->created_on } @$comments :
                sort { $b->created_on <=> $a->created_on } @$comments;
	    # filter out comments from unapproved commenters
	    @comments = grep { $_->visible() } @comments;
	    
            my $max = $n - 1 > $#comments ? $#comments : $n - 1;
            @comments = $so eq 'ascend' ?
                @comments[$#comments-$max..$#comments] :
                @comments[0..$max];
        } else {
            require MT::Comment;
            @comments = MT::Comment->load({ blog_id => $blog_id,
					    visible => 1 },
                { 'sort' => 'created_on',
                  direction => 'descend',
                  limit => $n });
            @comments = $so eq 'ascend' ?
                sort { $a->created_on <=> $b->created_on } @comments :
                sort { $b->created_on <=> $a->created_on } @comments;
        }
    } else {
        my $e = $ctx->stash('entry')
            or return $_[0]->_no_entry_error('MTComments');
        my $comments = $e->comments;
        @comments = $so eq 'ascend' ?
            sort { $a->created_on <=> $b->created_on } @$comments :
            sort { $b->created_on <=> $a->created_on } @$comments;
    }
    my $html = '';
    my $builder = $ctx->stash('builder');
    my $tokens = $ctx->stash('tokens');
    my $i = 1;
    
    @comments = grep { $_->visible() } @comments;

    for my $c (@comments) {
        $ctx->stash('comment' => $c);
        local $ctx->{current_timestamp} = $c->created_on;
        $ctx->stash('comment_order_num', $i);
        my $out = $builder->build($ctx, $tokens,
            { CommentsHeader => $i == 1,
              CommentsFooter => ($i == scalar @comments), %$cond } );
        return $ctx->error( $builder->errstr ) unless defined $out;
        $html .= $out;
        $i++;
    }
    if (!@comments) {
        return _hdlr_pass_tokens_else(@_);
    }
    $html;
}
sub _hdlr_comment_date {
    my $c = $_[0]->stash('comment')
        or return $_[0]->_no_comment_error('MTCommentDate');
    my $args = $_[1];
    $args->{ts} = $c->created_on;
    _hdlr_date($_[0], $args);
}
sub _hdlr_comment_id {
    my $args = $_[1];
    my $c = $_[0]->stash('comment')
        or return $_[0]->_no_comment_error('MTCommentID');
    $args && $args->{pad} ? (sprintf "%06d", $c->id) : $c->id;
}
sub _hdlr_comment_entry_id {
    my $args = $_[1];
    my $c = $_[0]->stash('comment')
        or return $_[0]->_no_comment_error('MTCommentEntryID');
    $args && $args->{pad} ? (sprintf "%06d", $c->entry_id) : $c->entry_id;
}
sub _hdlr_comment_author {
    sanitize_on($_[1]);
    my $tag = $_[0]->stash('tag');
    my $c = $_[0]->stash($tag =~ /Preview/ ? 'comment_preview' : 'comment')
        or return $_[0]->_no_comment_error('MT' . $tag);
    my $a = defined $c->author ? $c->author : '';
    $a ||= $_[1]{default} || '';
    remove_html($a);
}
sub _hdlr_comment_ip {
    my $tag = $_[0]->stash('tag');
    my $c = $_[0]->stash($tag =~ /Preview/ ? 'comment_preview' : 'comment')
        or return $_[0]->_no_comment_error('MT' . $tag);
    defined $c->ip ? $c->ip : '';
}
sub _hdlr_comment_author_link {
    #sanitize_on($_[1]);
    my($ctx, $args) = @_;
    my $tag = $ctx->stash('tag');
    my $c = $ctx->stash($tag =~ /Preview/ ? 'comment_preview' : 'comment')
        or return $ctx->_no_comment_error('MT' . $tag);
    my $name = $c->author;
    $name = '' unless defined $name;
    $name ||= $_[1]{default_name};
    $name ||= '';
    my $show_email = $args->{show_email} ? 1 : 0;
    my $show_url = 1 unless exists $args->{show_url} && !$args->{show_url};
    # TBD: new_window="1" arg
    if ($show_url && $c->url) {
        my $cfg = MT::ConfigMgr->instance;
        my $cgi_path = $cfg->CGIPath;
        $cgi_path =~ s#([^/])$#$1/#;
        my $comment_script = $cfg->CommentScript;
        $name = remove_html($name);
        my $url = remove_html($c->url);
        $url =~ s/>/&gt;/g;
        if ($c->id && !$args->{no_redirect}) {
            return sprintf(qq(<a title="%s" href="%s%s?__mode=red;id=%d">%s</a>),
                           $url, $cgi_path, $comment_script, $c->id, $name);
        } else {
            # In the case of preview, show URL directly without a redirect
            return sprintf(qq(<a title="%s" href="%s">%s</a>),
                           $url, $url, $name); 
        }
    } elsif ($show_email && $c->email && MT::Util::is_valid_email($c->email)) {
        my $email = remove_html($c->email);
        my $str = "mailto:" . $email;
        $str = spam_protect($str) if $args->{'spam_protect'};
        return sprintf qq(<a href="%s">%s</a>), $str, $name;
    } else {
        return $name;
    }
}
sub _hdlr_comment_email {
    sanitize_on($_[1]);
    my $tag = $_[0]->stash('tag');
    my $c = $_[0]->stash($tag =~ /Preview/ ? 'comment_preview' : 'comment')
        or return $_[0]->_no_comment_error('MT' . $tag);
    return '' unless defined $c->email;
    return '' unless $c->email =~ m/@/;
    my $email = remove_html($c->email);
    $_[1] && $_[1]->{'spam_protect'} ? spam_protect($email) : $email;
}
sub _hdlr_comment_author_identity {
     my ($ctx, $args) = @_;
     my $tag = $ctx->stash('tag');
     my $cmt = $ctx->stash('comment')
         or return $ctx->_no_comment_error('MT' . $tag);
    if ($cmt->commenter_id) {
	my $auth = MT::Author->load($cmt->commenter_id, {cached_ok=>1}) 
            or return "?";
	my $cfg = MT::ConfigMgr->instance();
	my $link = $cfg->IdentityURL;
	$link =~ s@/$@@;
	$link .= "/" . $auth->name();
 	my $blog = MT::Blog->load($ctx->stash('blog_id'), {cached_ok=>1});
 	my $root_url = $cfg->PublishCommenterIcon
            ? $blog->site_url()
            : ($cfg->StaticWebPath || $cfg->CGIPath) . "images";
        $root_url =~ s|/$||;
        qq{<a class="commenter-profile" href=\"$link\"><img alt='[TypeKey Profile Page]' src='$root_url/nav-commenters.gif' width='22' height='15' /></a>};
    } else {
	"";
    }
}
sub _hdlr_comment_url {
    sanitize_on($_[1]);
    my $tag = $_[0]->stash('tag');
    my $c = $_[0]->stash($tag =~ /Preview/ ? 'comment_preview' : 'comment')
        or return $_[0]->_no_comment_error('MT' . $tag);
    my $url = defined $c->url ? $c->url : '';
    remove_html($url);
}
sub _hdlr_comment_body {
    my($ctx, $arg) = @_;
    sanitize_on($arg);
    my $tag = $ctx->stash('tag');
    my $c = $ctx->stash($tag =~ /Preview/ ? 'comment_preview' : 'comment')
        or return $ctx->_no_comment_error('MT' . $tag);
    my $blog = $ctx->stash('blog');
    my $t = defined $c->text ? $c->text : '';
    $t = munge_comment($t, $blog)
        unless exists $arg->{autolink} && !$arg->{autolink};
    my $convert_breaks = exists $arg->{convert_breaks} ?
        $arg->{convert_breaks} :
        $blog->convert_paras_comments;
    return $convert_breaks ?
        MT->apply_text_filters($t, $blog->comment_text_filters, $ctx) :
        $t;
}
sub _hdlr_comment_order_num { $_[0]->stash('comment_order_num') }
sub _hdlr_comment_prev_state { $_[0]->stash('comment_state') }
sub _hdlr_comment_prev_static {
    my $s = $_[0]->stash('comment_is_static');
    defined $s ? $s : ''
}
sub _hdlr_comment_entry {
    my($ctx, $args, $cond) = @_;
    my $c = $ctx->stash('comment')
        or return $ctx->_no_comment_error('MTCommentEntry');
    my $entry = MT::Entry->load($c->entry_id, {cached_ok=>1})
        or return '';
    local $ctx->{__stash}{entry} = $entry;
    local $ctx->{current_timestamp} = $entry->created_on;
    $ctx->stash('builder')->build($ctx, $ctx->stash('tokens'), $cond);
}
sub _hdlr_commenter_name_thunk {
    my $ctx = shift;
    my $cfg = MT::ConfigMgr->instance;
    my $blog = $ctx->stash('blog') || MT::Blog->load($ctx->stash('blog_id'), {cached_ok=>1});
    my ($blog_domain) = $blog->archive_url =~ m|://([^/]*)|;
    my ($mt_domain) = $cfg->CGIPath =~ m|://([^/]*)|;
    $mt_domain ||= '';
    if ($blog_domain ne $mt_domain) {
        my $cgi_path = $cfg->CGIPath;
        $cgi_path .= '/' unless $cgi_path =~ m!/$!;
        my $cmt_script = $cfg->CommentScript;
        return "<script type='text/javascript' src='$cgi_path$cmt_script?__mode=cmtr_name_js'></script>";
    } else {
        return "<script type='text/javascript'>var commenter_name = getCookie('commenter_name')</script>";
    }
}
sub _hdlr_commenter_name {
    my $a = $_[0]->stash('commenter');
    $a ? $a->name || '' : '';
}
sub _hdlr_commenter_email {
    my $a = $_[0]->stash('commenter');
    return '' if $a && $a->email !~ m/@/;
    $a ? $a->email || '' : '';
}
sub _hdlr_commenter_trusted {
    my $a = $_[0]->stash('commenter');
    return '' unless $a;
    if ($a->trusted) {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}
sub _hdlr_feedback_score {
    my $fb = $_[0]->stash('comment') || $_[0]->stash('ping');
    $fb ? $fb->junk_score || 0 : '';
}

## Archives

{
    my $cur;
    sub type_handlers {
        {
        Individual => {
            group_end => sub { 1 },
            section_title => sub { $_[2]->title },
            section_timestamp => sub { $_[1] },
        },

        Daily => {
            group_end => sub {
		my $stamp = ref $_[1] ? $_[1]->created_on : $_[1];
                my $sod = start_end_day($stamp,
                    $_[0]->stash('blog'));
                my $end = !$cur || $sod == $cur ? 0 : 1;
                $cur = $sod;
                $end;
            },
            section_title => sub {
		my $stamp = ref $_[2] ? $_[2]->created_on : $_[2];
                my $start =
                    start_end_day($stamp, $_[0]->stash('blog'));
                _hdlr_date($_[0], { ts => $start, 'format' => ($_[1]->{format} || "%x") });
            },
            section_timestamp => sub {
		my $period_start = (ref $_[1]
				    ? sprintf("%04d%02d%02d000000", @{$_[1]})
				    : $_[1]);
                start_end_day($period_start, $_[0]->stash('blog'))
            },
            helper => \&start_end_day,
        },

        Weekly => {
            group_end => sub {
		my $stamp = ref $_[1] ? $_[1]->created_on : $_[1];
                my $sow = start_end_week($stamp, $_[0]->stash('blog'));
                my $end = !$cur || $sow == $cur ? 0 : 1;
                $cur = $sow;
                $end;
            },
            section_title => sub {
		my $stamp = ref $_[2] ? $_[2]->created_on : $_[2];
                my($start, $end) =
                    start_end_week($stamp, $_[0]->stash('blog'));
                my $format = $_[1]->{format} || '%x';
                _hdlr_date($_[0], { ts => $start, 'format' => $format }) .
                ' - ' .
                _hdlr_date($_[0], { ts => $end, 'format' => $format });
            },
            section_timestamp => sub {
		my ($y, $m, $d);
		if (ref $_[1] eq 'ARRAY') {
                    my ($stamp) = @{$_[1]};
                    my $yr = int($stamp / 100);
                    my $week = $stamp % 100;
		    ($y, $m, $d) = week2ymd($yr, $week);
		    start_end_week(sprintf("%04d%02d%02d000000", $y, $m, $d),
		      $_[0]->stash('blog'));
		} else {
		    start_end_week(ref $_[1] ? $_[1]->created_on : $_[1],
				   $_[0]->stash('blog'));
		}
            },
            helper => \&start_end_week,
        },

        Monthly => {
            group_end => sub {
		my $stamp = ref $_[1] ? $_[1]->created_on : $_[1];
                my $som = start_end_month($stamp,
                    $_[0]->stash('blog'));
                my $end = !$cur || $som == $cur ? 0 : 1;
                $cur = $som;
                $end;
            },
            section_title => sub {
		my $stamp = ref $_[2] ? $_[2]->created_on : $_[2];
                my $start =
                    start_end_month($stamp, $_[0]->stash('blog'));
                _hdlr_date($_[0], { ts => $start, 'format' => $_[1]->{format} || "%B %Y" });
            },
            section_timestamp => sub {
		my $period_start = ref $_[1] ? sprintf("%04d%02d%02d000000",
						       @{$_[1]}, 1)
		                             : $_[1];
                start_end_month($period_start, $_[0]->stash('blog'));
            },
            helper => \&start_end_month,
        },
        };
    }

    sub _hdlr_archive_prev_next {
        my($ctx, $args, $cond) = @_;
        my $tag = $ctx->stash('tag');
        my $is_prev = $tag eq 'ArchivePrevious';
        my $ts = $ctx->{current_timestamp}
            or return $ctx->error(MT->translate(
               "You used an [_1] without a date context set up.", "<MT$tag>" ));
        my $at = $_[1]->{archive_type} || $ctx->{current_archive_type};
        return $ctx->error(MT->translate(
            "[_1] can be used only with Daily, Weekly, or Monthly archives.",
            "<MT$tag>" ))
            unless $at eq 'Daily' || $at eq 'Weekly' || $at eq 'Monthly';
        my $res = '';
        my @arg = ($ts, $ctx->stash('blog_id'), $at);
        push @arg, $is_prev ? 'previous' : 'next';
        my $hdlrs = $ctx->type_handlers();
        my $helper = $hdlrs->{$at}{helper};
        if (my $entry = get_entry(@arg)) {
            my $builder = $ctx->stash('builder');
            local $ctx->{__stash}->{entries} = [ $entry ];
            my($start, $end) = $helper->($entry->created_on);
            local $ctx->{current_timestamp} = $start;
            local $ctx->{current_timestamp_end} = $end;
            defined(my $out = $builder->build($ctx, $ctx->stash('tokens'),
                $cond))
                or return $ctx->error( $builder->errstr );
            $res .= $out;
        }
        $res;
    }

    sub _hdlr_index_list {
        my ($ctx, $args, $cond) = @_;
        my $tokens = $ctx->stash('tokens');
        my $builder = $ctx->stash('builder');
        my $iter = MT::Template->load_iter({ type => 'index',
                                             blog_id => $ctx->stash('blog_id') });
        my $res = '';
        while (my $tmpl = $iter->()) {
            local $ctx->{__stash}{'index'} = $tmpl;
            defined(my $out = $builder->build($ctx, $tokens, $cond)) or
                return $ctx->error( $builder->errstr );
            $res .= $out;
        }
        $res;
    }

    sub _hdlr_index_link {
        my ($ctx, $args, $cond) = @_;
        my $idx = $ctx->stash('index');
        return '' unless $idx;
        my $blog = $ctx->stash('blog');
        my $path = $blog->site_url;
        $path .= '/' unless $path =~ m!/$!;
        $path .= $idx->outfile;
        $path = MT::Util::strip_index($path, $blog) unless $args->{with_index};
        $path;
    }
    sub _hdlr_index_name {
        my ($ctx, $args, $cond) = @_;
        my $idx = $ctx->stash('index');
        return '' unless $idx;
        $idx->name || '';
    }
    sub _hdlr_index_basename {
        my ($ctx, $args, $cond) = @_;
        my $name = MT->instance->config('IndexBasename');
        if (!$args->{extension}) {
            return $name;
        }
        my $blog = $ctx->stash('blog');
        my $ext = $blog->file_extension;
        $ext = '.' . $ext if $ext;
        $name . $ext;
    }

    sub _hdlr_archive_set {
        my($ctx, $args, $cond) = @_;
        my $blog = $ctx->stash('blog');
        my $at;
        if ($args->{archive_type}) {
            $at = $args->{archive_type};
        } else {
            $at = $blog->archive_type;
        }
        return '' if !$at || $at eq 'None';
        my @at = split /,/, $at;
        my $res = '';
        my $tokens = $ctx->stash('tokens');
        my $builder = $ctx->stash('builder');
        my $old_at = $blog->archive_type_preferred();
        foreach my $type (@at) {
            $blog->archive_type_preferred($type);
            defined(my $out = $builder->build($ctx, $tokens, $cond)) or
                return $ctx->error( $builder->errstr );
            $res .= $out;
        }
        $blog->archive_type_preferred($old_at);
        $res;
    }

    sub _hdlr_archives {
        my($ctx, $args, $cond) = @_;
        $cur = undef;
        my $blog = $ctx->stash('blog');
        my $at = $blog->archive_type;
        return '' if !$at || $at eq 'None';
        if (my $arg_at = $args->{archive_type}) {
            #my %at = map { $_ => 1 } split /,/, $at;
            #return '' unless ($at{$arg_at});
            $at = $arg_at;
        } elsif ($blog->archive_type_preferred) {
            $at = $blog->archive_type_preferred;
        } else {
            $at = (split /,/, $at)[0];
        }
        local $ctx->{current_archive_type} = $at;
        ## If we are producing a Category archive list, don't bother to
        ## handle it here--instead hand it over to <MTCategories>.
        return _hdlr_categories(@_) if $at eq 'Category';
        my %args;
        if ($at eq 'Category') {
            $args{'sort'} = 'category_id';
        } else {
            $args{'sort'} = 'created_on';
            $args{direction} = 'descend';
        }
        my $hdlrs = $ctx->type_handlers();
        my $group_end = $hdlrs->{$at}{group_end};
        my $sec_ts = $hdlrs->{$at}{section_timestamp};
	my $tokens = $ctx->stash('tokens');
	my $builder = $ctx->stash('builder');
	my $res = '';
	my $i = 0;
	my $n = $args->{lastn};

	use constant SPEEDUP_ENABLED => 1;

	if (MT::ConfigMgr->instance()->ObjectDriver =~ /DBI/
	    && MT::ConfigMgr->instance()->ObjectDriver !~ /sqlite/
	    && ($at ne 'Individual') && SPEEDUP_ENABLED)
	{
	    my $group_iter;
	    if ($at eq 'Daily') {
		$group_iter = MT::Entry->count_group_by({blog_id => $blog->id,
						 status => MT::Entry::RELEASE()},
				    {group=>["extract(year from created_on)",
					     "extract(month from created_on)",
					     "extract(day from created_on)"],
				    sort=>"extract(year from created_on) desc,
					   extract(month from created_on) desc,
					   extract(day from created_on) desc"})
		    or return $ctx->error(MT->translate("Couldn't get daily archive list"));
	    } elsif ($at eq 'Monthly') {
		$group_iter = MT::Entry->count_group_by({blog_id => $blog->id,
						 status => MT::Entry::RELEASE()},
				   {group=>["extract(year from created_on)",
					    "extract(month from created_on)"],
				   sort=>"extract(year from created_on) desc,
					  extract(month from created_on) desc"})
		    or return $ctx->error(MT->translate("Couldn't get monthly archive list"));
	    } elsif ($at eq 'Weekly') {
		$group_iter = MT::Entry->count_group_by({blog_id => $blog->id,
						 status => MT::Entry::RELEASE()},
				   {group=>["week_number"],
				   sort=>"week_number desc"})
		    or return $ctx->error(MT->translate("Couldn't get weekly archive list"));
	    } else {
		return $ctx->error(MT->translate("Unknown archive type [_1] in <MTArchiveList>", $at));
	    }
	    return $ctx->error(MT->translate("Group iterator failed."))
		unless defined($group_iter);
	    my ($cnt, @grp);
            my $first = 1; my $last = 0;
            my ($next_cnt, @next_grp) = $group_iter->();
	    while ((($cnt, @grp) = ($next_cnt, @next_grp)) && defined($cnt)) {
		my($start, $end) = $sec_ts->($ctx, \@grp);
                $i++;
                ($next_cnt, @next_grp) = $group_iter->();
                $last = 1 if $n && ($i >= $n);
                $last = 1 unless $next_cnt;
		local $ctx->{current_timestamp} = $start;
		local $ctx->{current_timestamp_end} = $end;
		local $ctx->{__stash}{entries} = delay(sub{ 
                    my @entries = MT::Entry->load(
			       {blog_id => ref $blog ? $blog->id : $blog,
                                status => MT::Entry::RELEASE(),
				created_on => [$ctx->{current_timestamp},
					       $ctx->{current_timestamp_end}]},
						  {range => {created_on => 1}});
		    \@entries;
		});
		defined(my $out = $builder->build($ctx, $tokens, { %$cond, ArchiveListHeader => $first, ArchiveListFooter => $last })) or
		    return $ctx->error( $builder->errstr );
		$res .= $out;
                $first = 0;
		last if $last;
	    }
	} else {
	    my $iter = MT::Entry->load_iter({ blog_id => $blog->id,
					      status => MT::Entry::RELEASE() },
					    \%args);
	    my @entries;
	    my $build_archive_item = sub {
		my ($entries, $extra_cond) = @_;
		local $ctx->{__stash}{entries} = $entries;
		my($start, $end) = $sec_ts->($ctx, (ref $entries->[0] ? $entries->[0]->created_on : ""));
		local $ctx->{current_timestamp} = $start;
		local $ctx->{current_timestamp_end} = $end;
                defined(my $out = $builder->build($ctx, $tokens, { %$cond, %$extra_cond })) or
		    return $ctx->error( $builder->errstr );
		$res .= $out;
	    };
	    # Here we build groups of entries; every time we come
	    # across one that satisfies group_end, we build the arvhie
	    # item for the existing group, and clear the list.
            my $first = 1;
            my $last = 0;
	    while (my $entry = $iter->()) {
		if ($group_end->($ctx, $entry) && @entries) {
                    $i++;
		    $last = 1 if $n && ($i >= $n);
		    &$build_archive_item(\@entries, { ArchiveListHeader => $first, ArchiveListFooter => $last } );
		    @entries = ();                       ## clear the entry list
                    $first = 0;
		    last if $last;
		}
		push @entries, $entry;
	    }
	    if (@entries) {
		&$build_archive_item(\@entries, { ArchiveListHeader => $first,
                    ArchiveListFooter => 1 });
	    }
	}
	$res;
    }

    sub _hdlr_archive_title {
        ## Since this tag can be called from inside <MTCategories>,
        ## we need a way to map this tag to <$MTCategoryLabel$>.
        return _hdlr_category_label(@_) if $_[0]->{inside_mt_categories};

        my($ctx, $args) = @_;
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
            my $hdlrs = $ctx->type_handlers();
            my $st = $hdlrs->{$ctx->{current_archive_type}}{section_title};
	    my $title = (@entries && $entries[0]) ? $st->($ctx, $args, $entries[0])
		: $st->($ctx, $args, $ctx->{current_timestamp});
            defined $title ? $title : '';
        }
    }
}

sub _hdlr_archive_date_end {
    my($ctx) = @_;
    my $end = $ctx->{current_timestamp_end}
        or return $_[0]->error(MT->translate(
            "You used an [_1] tag outside of a Daily, Weekly, or Monthly " .
            "context.", '<$MTArchiveDateEnd$>' ));
    $_[1]{ts} = $end;
    _hdlr_date(@_);
}

sub _hdlr_archive_type {
    my ($ctx, $args, $cond) = @_;

    my $at = $ctx->{archive_type} || $ctx->{current_archive_type};
    $at = 'Category' if $ctx->{inside_mt_categories};
    $at;
}

sub _hdlr_archive_file {
    my ($ctx, $args, $cond) = @_;

    my $at = $ctx->{archive_type} || $ctx->{current_archive_type};
    $at = 'Category' if $ctx->{inside_mt_categories};
    my $f;
    if (!$at || $at eq 'Individual') {
        my $e = $ctx->stash('entry');
        unless ($e) {
            my $entries = $ctx->stash('entries');
            $e = $entries->[0];
        }
        return $ctx->error(MT->translate("Could not determine entry")) if !$e;
        $f = $e->basename;
    } else {
        $f = MT::ConfigMgr->instance->IndexBasename;
    }
    if (exists $args->{extension} && !$args->{extension}) {
    } else {
        my $blog = $ctx->stash('blog');
        if (my $ext = $blog->file_extension) {
            $f .= '.' . $ext;
        }
    }
    $f;
}

sub _hdlr_archive_link {
    ## Since this tag can be called from inside <MTCategories>,
    ## we need a way to map this tag to <$MTCategoryArchiveLink$>.
    return _hdlr_category_archive(@_) if $_[0]->{inside_mt_categories};

    my($ctx) = @_;

    my $blog = $ctx->stash('blog');
    my $types = ',' . $blog->archive_type . ',';
    my $entries = force($ctx->stash('entries'));
    if (!$entries && (my $e = $ctx->stash('entry'))) {
        push @$entries, $e;
    }

    return $ctx->error(MT->translate(
        "You used an [_1] tag outside of the proper context.",
        '<$MTArchiveLink$>' ))
        unless ($ctx->{current_timestamp} ||
		($entries && ref($entries)) eq 'ARRAY');
    # We assume there's an entry, but if there's no entry, 
    #   archive_file_for will use the current_timestamp instead
    my $entry = $entries->[0];
    my $at = $_[1]->{archive_type} || $ctx->{current_archive_type};
    return $ctx->error(MT->translate(
        "You used an [_1] tag for linking into '[_2]' archives, but that archive type is not published.", '<$MTArchiveLink$>', $at))
        unless $types =~ m/\Q$at\E/;
    my $arch = $blog->archive_url;
    $arch .= '/' unless $arch =~ m!/$!;
    $arch .= archive_file_for($entry, $blog, $at, undef, undef,
                              $ctx->{current_timestamp});
    $arch = MT::Util::strip_index($arch, $blog) unless $_[1]->{with_index};
    $arch;
}

sub _hdlr_archive_count {
    my $ctx = $_[0];
    if ($ctx->{inside_mt_categories}) {
        return _hdlr_category_count($ctx);
    } elsif (my $count = $ctx->stash('archive_count')) {
        return $count;
    } else {
        my $e = force($_[0]->stash('entries'));
	my @entries = @$e if ref($e) eq 'ARRAY';
	return scalar @entries;
    }
}

sub _hdlr_archive_category {
    &_hdlr_category_label;
}

sub _hdlr_image_url { $_[0]->stash('image_url') }
sub _hdlr_image_width { $_[0]->stash('image_width') }
sub _hdlr_image_height { $_[0]->stash('image_height') }

sub _hdlr_calendar {
    my($ctx, $args, $cond) = @_;
    my $blog_id = $ctx->stash('blog_id');
    my($prefix);
    my @ts = offset_time_list(time, $blog_id);
    my $today = sprintf "%04d%02d", $ts[5]+1900, $ts[4]+1;
    if ($prefix = $args->{month}) {
        if ($prefix eq 'this') {
            my $ts = $ctx->{current_timestamp}
                or return $ctx->error(MT->translate(
                    "You used an [_1] tag without a date context set up.",
                    qq(<MTCalendar month="this">) ));
            $prefix = substr $ts, 0, 6;
        } elsif ($prefix eq 'last') {
            my $year = substr $today, 0, 4;
            my $month = substr $today, 4, 2;
            if ($month - 1 == 0) {
                $prefix = $year - 1 . "12";
            } else {
                $prefix = $year . $month - 1;
            }
        } else {
            return $ctx->error(MT->translate(
                "Invalid month format: must be YYYYMM" ))
                unless length($prefix) eq 6;
        }
    } else {
        $prefix = $today;
    }
    my($cat_name, $cat);
    if ($cat_name = $args->{category}) {
        $cat = MT::Category->load({ label => $cat_name, blog_id => $blog_id })
            or return $ctx->error(MT->translate(
                "No such category '[_1]'", $cat_name ));
    } else {
        $cat_name = '';    ## For looking up cached calendars.
    }
    my $uncompiled = $ctx->stash('uncompiled');
    my $r = MT::Request->instance;
    my $calendar_cache = $r->cache('calendar');
    unless ($calendar_cache) {
        $r->cache('calendar', $calendar_cache = { });
    }
    if (exists $calendar_cache->{$prefix . $cat_name} &&
        $calendar_cache->{$prefix . $cat_name}{'uc'} eq $uncompiled) {
        return $calendar_cache->{$prefix . $cat_name}{output};
    }
    $today .= sprintf "%02d", $ts[3];
    my($start, $end) = start_end_month($prefix);
    my($y, $m) = unpack 'A4A2', $prefix;
    my $days_in_month = days_in($m, $y);
    my $pad_start = wday_from_ts($y, $m, 1);
    my $pad_end = 6 - wday_from_ts($y, $m, $days_in_month);
    my $iter = MT::Entry->load_iter({ blog_id => $blog_id,
                                      created_on => [ $start, $end ],
                                      status => MT::Entry::RELEASE() },
        { range => { created_on => 1 },
          'sort' => 'created_on',
          direction => 'ascend', });
    my @left;
    my $res = '';
    my $tokens = $ctx->stash('tokens');
    my $builder = $ctx->stash('builder');
    my $iter_drained = 0;
    for my $day (1..$pad_start+$days_in_month+$pad_end) {
        my $is_padding =
            $day < $pad_start+1 || $day > $pad_start+$days_in_month;
        my($this_day, @entries) = ('');
        local($ctx->{__stash}{entries}, $ctx->{__stash}{calendar_day},
              $ctx->{current_timestamp});
        local $ctx->{__stash}{calendar_cell} = $day;
        unless ($is_padding) {
            $this_day = $prefix . sprintf("%02d", $day - $pad_start);
            my $no_loop = 0;
            if (@left) {
                if (substr($left[0]->created_on, 0, 8) eq $this_day) {
                    @entries = @left;
                    @left = ();
                } else {
                    $no_loop = 1;
                }
            }
            unless ($no_loop || $iter_drained) {
                while (my $entry = $iter->()) {
                    next unless !$cat || $entry->is_in_category($cat);
                    my $e_day = substr $entry->created_on, 0, 8;
                    push(@left, $entry), last
                        unless $e_day eq $this_day;
                    push @entries, $entry;
                }
                $iter_drained++ unless @left;
            }
            $ctx->{__stash}{entries} = delay(sub{\@entries});
            $ctx->{current_timestamp} = $this_day . '000000';
            $ctx->{__stash}{calendar_day} = $day - $pad_start;
        }
        defined(my $out = $builder->build($ctx, $tokens, {
            %$cond,
            CalendarWeekHeader => ($day-1) % 7 == 0,
            CalendarWeekFooter => $day % 7 == 0,
            CalendarIfEntries => !$is_padding && scalar @entries,
            CalendarIfNoEntries => !$is_padding && !(scalar @entries),
            CalendarIfToday => ($today eq $this_day),
            CalendarIfBlank => $is_padding,
        })) or
            return $ctx->error( $builder->errstr );
        $res .= $out;
    }
    $calendar_cache->{$prefix . $cat_name} =
        { output => $res, 'uc' => $uncompiled };
    $res;
}

sub _hdlr_calendar_day {
    my $day = $_[0]->stash('calendar_day')
        or return $_[0]->error(MT->translate(
            "You used an [_1] tag outside of the proper context.",
            '<$MTCalendarDay$>' ));
    $day;
}

sub _hdlr_calendar_cell_num {
    my $num = $_[0]->stash('calendar_cell')
        or return $_[0]->error(MT->translate(
            "You used an [_1] tag outside of the proper context.",
            '<$MTCalendarCellNumber$>' ));
    $num;
}

sub _hdlr_categories {
    my($ctx, $args, $cond) = @_;
    my $blog_id = $ctx->stash('blog_id');
    require MT::Placement;
    my $iter = MT::Category->load_iter({ blog_id => $blog_id },
        { 'sort' => 'label', direction => 'ascend' });
    my $res = '';
    my $builder = $ctx->stash('builder');
    my $tokens = $ctx->stash('tokens');
    my $needs_entries = ($ctx->stash('uncompiled') =~ /<\$?MTEntries/) ? 1 : 0;
    ## In order for this handler to double as the handler for
    ## <MTArchiveList archive_type="Category">, it needs to support
    ## the <$MTArchiveLink$> and <$MTArchiveTitle$> tags
    local $ctx->{inside_mt_categories} = 1;
    while (my $cat = $iter->()) {
        local $ctx->{__stash}{category} = $cat;
        local $ctx->{__stash}{entries};
        local $ctx->{__stash}{category_count};
        my @args = (
            { blog_id => $blog_id,
              status => MT::Entry::RELEASE() },
            { 'join' => [ 'MT::Placement', 'entry_id',
                          { category_id => $cat->id } ],
              'sort' => 'created_on',
              direction => 'descend', });
        if ($needs_entries) {
            my @entries = MT::Entry->load(@args);
            $ctx->{__stash}{entries} = delay(sub{\@entries});
            $ctx->{__stash}{category_count} = scalar @entries;
        } else {
            $ctx->{__stash}{category_count} = MT::Entry->count(@args);
        }
        next unless $ctx->{__stash}{category_count} || $args->{show_empty};
        defined(my $out = $builder->build($ctx, $tokens, $cond))
            or return $ctx->error( $builder->errstr );
        $res .= $out;
    }
    $res;
}

sub _hdlr_category_id {
    my $cat = ($_[0]->stash('category') || $_[0]->stash('archive_category'))
        or return $_[0]->error(MT->translate(
            "You used an [_1] tag outside of the proper context.",
            '<$MTCategoryID$>' ));
    $cat->id;
}

sub _hdlr_category_label {
    my ($ctx, $args, $cond) = @_;
    my $e = $ctx->stash('entry');
    my $cat = ($ctx->stash('category') || $ctx->stash('archive_category'))
        || (($e = $ctx->stash('entry')) && $e->category)
        or return (defined($args->{default}) ? $args->{default} : 
                    $ctx->error(MT->translate(
                           "You used an [_1] tag outside of the proper context.",
                           '<$MTCategoryLabel$>' )));
    my $label = $cat->label || '';
    if ($args->{dirify}) {
        $label = dirify($label, $args->{dirify});
        if ($label !~ m/\w/) {
            $label = 'cat' . $cat->id;
        }
        # prevent global dirify handler
        delete $args->{dirify};
    }
    $label;
}

sub _hdlr_category_desc {
    my $cat = ($_[0]->stash('category') || $_[0]->stash('archive_category'))
        or return $_[0]->error(MT->translate('You used <$MTCategoryDescription$> outside of the proper context.'));
    defined $cat->description ? $cat->description : '';
}

sub _hdlr_category_count {
    my($ctx) = @_;
    my $cat = ($ctx->stash('category') || $_[0]->stash('archive_category'))
        or return $_[0]->error(MT->translate(
            "You used an [_1] tag outside of the proper context.",
            '<$MTCategoryCount$>' ));
    my($count);
    unless ($count = $ctx->stash('category_count')) {
        my @args = ({ blog_id => $ctx->stash ('blog_id'),
                      status => MT::Entry::RELEASE() },
                    { 'join' => [ 'MT::Placement', 'entry_id',
                                  { category_id => $cat->id } ] });
        require MT::Placement;
        $count = scalar MT::Entry->count(@args);
    }
    $count;
}

sub _hdlr_category_archive {
    my $cat = ($_[0]->stash('category') || $_[0]->stash('archive_category'))
        or return $_[0]->error(MT->translate(
            "You used an [_1] tag outside of the proper context.",
            '<$MTCategoryArchiveLink$>' ));
    my $blog = $_[0]->stash('blog');
    my $at = $blog->archive_type;
    return $_[0]->error(MT->translate(
        '[_1] can be used only if you have enabled Category archives.',
        '<$MTCategoryArchiveLink$>' ))
            unless $at =~ /Category/;
    my $arch = $blog->archive_url;
    $arch .= '/' unless $arch =~ m!/$!;
    $arch = $arch . archive_file_for(undef, $blog, 'Category', $cat);
    $arch = MT::Util::strip_index($arch, $blog) unless $_[1]->{with_index};
    $arch;
}

sub _hdlr_category_tb_link {
    my($ctx, $args) = @_;
    my $cat = $_[0]->stash('category') || $_[0]->stash('archive_category');
    if (!$cat) {
        my $cat_name = $args->{category}
            or return $ctx->error(MT->translate('<$MTCategoryTrackbackLink$> must be ' .
                "used in the context of a category, or with the 'category' " .
                "attribute to the tag."));
        $cat = MT::Category->load({ label => $cat_name,
                                    blog_id => $ctx->stash('blog_id') })
            or return $ctx->error(MT->translate("No such category '[_1]'", $cat_name));
    }
    require MT::Trackback;
    my $tb = MT::Trackback->load({ category_id => $cat->id })
        or return '';
    my $cfg = MT::ConfigMgr->instance;
    my $path = $cfg->CGIPath;
    $path .= '/' unless $path =~ m!/$!;
    $path . $cfg->TrackbackScript . '/' . $tb->id;
}

sub _hdlr_category_allow_pings {
    my $cat = $_[0]->stash('category') || $_[0]->stash('archive_category');
    if ($cat->allow_pings) {
        _hdlr_pass_tokens(@_);
    } else {
        _hdlr_pass_tokens_else(@_);
    }                                 
}

sub _hdlr_category_tb_count {
    my($ctx, $args) = @_;
    my $cat = $_[0]->stash('category') || $_[0]->stash('archive_category');
    return 0 unless $cat;
    require MT::Trackback;
    my $tb = MT::Trackback->load( { category_id => $cat->id } );
    return 0 unless $tb;
    require MT::TBPing;
    my $count = MT::TBPing->count( { tb_id => $tb->id, visible => 1 } );
    $count || 0;
}

sub _hdlr_google_search {
    my($ctx, $args, $cond) = @_;
    my $query;
    my $blog = $ctx->stash('blog');
    if ($query = $args->{query}) {
    } elsif (my $url = $args->{related}) {
        $query = 'related:' . ($url eq '1' ? $blog->site_url : $url);
    } elsif ($args->{title}) {
        $query = $ctx->_hdlr_entry_title or return '';
    } elsif ($args->{excerpt}) {
        $query = $ctx->_hdlr_entry_excerpt or return '';
    } elsif ($args->{keywords}) {
        $query = $ctx->_hdlr_entry_keywords or return '';
    } else {
        return $ctx->error(MT->translate(
            'You used [_1] without a query.', '<MTGoogleSearch>' ));
    }
    my $key = $blog->google_api_key
        or return $ctx->error(MT->translate(
            'You need a Google API key to use [_1]', '<MTGoogleSearch>' ));
    my $max = $args->{results} || 10;
    require SOAP::Lite;
    require File::Basename;
    ## Look for GoogleSearch.wsdl in the lib/MT directory.
    my $dir = $INC{'MT.pm'};
    $dir = File::Basename::dirname($dir);
    my $wsdl = File::Spec->catfile($dir, 'MT', 'GoogleSearch.wsdl');
    {
        ## Turn off warnings, because the following can cause a
        ## "subroutine redefined" warning.
        local $^W = 0;
        *SOAP::XMLSchema1999::Deserializer::as_boolean =
        *SOAP::XMLSchemaSOAP1_1::Deserializer::as_boolean =
        \&SOAP::XMLSchema2001::Deserializer::as_boolean;
    }
    my $result;
    eval {
        $result = SOAP::Lite->service('file:' . $wsdl)
                            ->doGoogleSearch($key, $query, 0, $max,
                             0, '', 0, '', 'latin1', 'latin1'
                             );
    };
    warn $@, return '' if $@;
    my $tokens = $ctx->stash('tokens');
    my $builder = $ctx->stash('builder');
    my $res = '';
    for my $rec (@{ $result->{resultElements} }) {
        $ctx->stash('google_result', $rec);
        my $out = $builder->build($ctx, $tokens, $cond);
        return $ctx->error( $builder->errstr ) unless defined $out;
        $res .= $out;
    }
    $res;
}

sub _hdlr_google_search_result {
    my($ctx, $args) = @_;
    my $res = $ctx->stash('google_result')
        or return $ctx->error(MT->translate(
           "You used an [_1] tag outside of the proper context.",
           '<$MTGoogleSearchResult$>' ));
    my $prop = $args->{property} || 'title';
    exists $res->{$prop}
        or return $ctx->error(MT->translate(
            'You used a non-existent property from the result structure.' ));
    $res->{$prop} || '';
}

sub _hdlr_pings {
    my($ctx, $args, $cond) = @_;
    require MT::Trackback;
    require MT::TBPing;
    my($tb, $cat);
    if (my $e = $ctx->stash('entry')) {
        $tb = MT::Trackback->load({ entry_id => $e->id });
        return '' unless $tb;
    } elsif ($cat = $ctx->stash('archive_category')) {
        $tb = MT::Trackback->load({ category_id => $cat->id });
        return '' unless $tb;
    } elsif (my $cat_name = $args->{category}) {
        $cat = MT::Category->load({ label => $cat_name,
                                    blog_id => $ctx->stash('blog_id') })
            or return $ctx->error(MT->translate("No such category '[_1]'", $cat_name));
        $tb = MT::Trackback->load({ category_id => $cat->id });
        return '' unless $tb;
    }
    my $res = '';
    my $builder = $ctx->stash('builder');
    my $tokens = $ctx->stash('tokens');
    my $sort_order = $args->{sort_order} || 'ascend';
    my %terms;
    $terms{tb_id} = $tb->id if $tb;
    $terms{blog_id} = $ctx->stash('blog_id');
    $terms{visible} = 1;
    my %arg = ('sort' => 'created_on', direction => $sort_order);
    if (my $limit = $args->{lastn}) {
        $arg{direction} = 'descend';
        $arg{limit} = $limit;
    }
    my $iter = MT::TBPing->load_iter(\%terms, \%arg);
    my $count = 0;
    my $next = $iter->();
    while (my $ping = $next) {
        $next = $iter->();
        $count++;
        $ctx->stash('ping' => $ping);
        local $ctx->{current_timestamp} = $ping->created_on;
        my $out = $builder->build($ctx, $tokens, { %$cond,
            PingsHeader => $count == 1, PingsFooter => !$next });
        return $ctx->error( $builder->errstr ) unless defined $out;
        $res .= $out;
    }
    $res;
}
sub _hdlr_pings_sent {
    my($ctx, $args, $cond) = @_;
    my $e = $ctx->stash('entry')
        or return $ctx->_no_entry_error('MTPingsSent');
    my $builder = $ctx->stash('builder');
    my $tokens = $ctx->stash('tokens');
    my $res = '';
    my $pings = $e->pinged_url_list;
    for my $url (@$pings) {
        $ctx->stash('ping_sent_url', $url);
        defined(my $out = $builder->build($ctx, $tokens, $cond))
            or return $ctx->error($builder->errstr);
        $res .= $out;
    }
    $res;
}
sub _hdlr_pings_sent_url { $_[0]->stash('ping_sent_url') }
sub _no_ping_error {
    return $_[0]->error(MT->translate(
    "You used an '[_1]' tag outside of the context of a ping; perhaps you mistakenly placed it outside of an 'MTPings' container?", $_[1]));
}
sub _hdlr_ping_date {
    my $p = $_[0]->stash('ping')
        or return $_[0]->_no_ping_error('MTPingDate');
    my $args = $_[1];
    $args->{ts} = $p->created_on;
    _hdlr_date($_[0], $args);
}
sub _hdlr_ping_id {
    my $ping = $_[0]->stash('ping')
        or return $_[0]->_no_ping_error('MTPingID');
    $ping->id;
}
sub _hdlr_ping_title {
    sanitize_on($_[1]);
    my $ping = $_[0]->stash('ping')
        or return $_[0]->_no_ping_error('MTPingTitle');
    defined $ping->title ? $ping->title : '';
}
sub _hdlr_ping_url {
    sanitize_on($_[1]);
    my $ping = $_[0]->stash('ping')
        or return $_[0]->_no_ping_error('MTPingURL');
    defined $ping->source_url ? $ping->source_url : '';
}
sub _hdlr_ping_excerpt {
    sanitize_on($_[1]);
    my $ping = $_[0]->stash('ping')
        or return $_[0]->_no_ping_error('MTPingExcerpt');
    defined $ping->excerpt ? $ping->excerpt : '';
}
sub _hdlr_ping_ip {
    my $ping = $_[0]->stash('ping')
        or return $_[0]->_no_ping_error('MTPingIP');
    defined $ping->ip ? $ping->ip : '';
}
sub _hdlr_ping_blog_name {
    sanitize_on($_[1]);
    my $ping = $_[0]->stash('ping')
        or return $_[0]->_no_ping_error('MTPingBlogName');
    defined $ping->blog_name ? $ping->blog_name : '';
}

sub _hdlr_if_allow_comment_html {
    my ($ctx, $args, $cond) = @_;
    my $blog = $ctx->stash('blog');
    return '' unless $blog;
    if ($blog->allow_comment_html) {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_if_comments_allowed {
    my ($ctx, $args, $cond) = @_;
    my $blog = $ctx->stash('blog');
    my $cfg = MT::ConfigMgr->instance;
    if ((!$blog || ($blog && ($blog->allow_unreg_comments
                              || ($blog->allow_reg_comments
                                  && $blog->effective_remote_auth_token))))
        && $cfg->AllowComments) {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

# comments exist in stash OR entry context allows comments
sub _hdlr_if_comments_active {
    my ($ctx, $args, $cond) = @_;
    my $blog = $ctx->stash('blog');
    my $cfg = MT::ConfigMgr->instance;
    my $active;
    if (my $entry = $ctx->stash('entry')) {
        $active = 1 if ($blog->accepts_comments && $entry->allow_comments
			&& $cfg->AllowComments);
        $active = 1 if $entry->comment_count;
    } else {
        $active = 1 if ($blog->accepts_comments && $cfg->AllowComments);
    }
    if ($active) {
	return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_if_comments_accepted {
    my ($ctx, $args, $cond) = @_;
    my $blog = $ctx->stash('blog');
    my $cfg = MT::ConfigMgr->instance;
    my $entry = $ctx->stash('entry');
    my $blog_comments_accepted = $blog->accepts_comments && $cfg->AllowComments;
    my $accepted = $blog_comments_accepted;
    $accepted = 0 if $entry && !$entry->allow_comments;
    if ($accepted) {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_if_pings_active {
    my ($ctx, $args, $cond) = @_;
    my $blog = $ctx->stash('blog');
    my $cfg = MT::ConfigMgr->instance;
    my $entry = $ctx->stash('entry');
    my $active;
    $active = 1 if $cfg->AllowPings && $blog->allow_pings;
    $active = 0 if $entry && !$entry->allow_pings;
    $active = 1 if !$active && $entry->ping_count;
    if ($active) {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_if_pings_accepted {
    my ($ctx, $args, $cond) = @_;
    my $blog = $ctx->stash('blog');
    my $cfg = MT::ConfigMgr->instance;
    my $accepted;
    my $entry = $ctx->stash('entry');
    $accepted = 1 if $blog->allow_pings && $cfg->AllowPings;
    $accepted = 0 if $entry && !$entry->allow_pings;
    if ($accepted) {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_if_pings_allowed {
    my ($ctx, $args, $cond) = @_;
    my $blog = $ctx->stash('blog');
    my $cfg = MT::ConfigMgr->instance;
    if ($blog->allow_pings && $cfg->AllowPings) {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

# FIXME: this is bogus
sub _hdlr_if_dynamic_comments {
    my ($ctx, $args, $cond) = @_;
    my $cfg = MT::ConfigMgr->instance;
    my $mt = MT->instance;
    if (!$mt->isa('MT::App::Comments') && $cfg->DynamicComments) {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_if_need_email {
    my ($ctx, $args, $cond) = @_;
    my $blog = $ctx->stash('blog');
    my $cfg = MT::ConfigMgr->instance;
    if ($blog->require_comment_emails) {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_entry_if_allow_comments {
    my ($ctx, $args, $cond) = @_;
    my $entry = $ctx->stash('entry');
    if ($entry->allow_comments) {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_entry_if_comments_open {
    my ($ctx, $args, $cond) = @_;
    my $blog = $ctx->stash('blog');
    my $entry = $ctx->stash('entry');
    my $cfg = MT::ConfigMgr->instance;
    if ($entry && $entry->allow_comments && $entry->allow_comments eq '1') {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_entry_if_allow_pings {
    my ($ctx, $args, $cond) = @_;
    my $entry = $ctx->stash('entry');
    if ($entry->allow_pings) {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_entry_if_extended {
    my ($ctx, $args, $cond) = @_;
    my $entry = $ctx->stash('entry');
    my $more = '';
    if ($entry) {
        $more = $entry->text_more;
        $more = '' unless defined $more;
        $more =~ s!(^\s+|\s+$)!!g;
    }
    if ($more ne '') {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_if_commenter_pending {
    my ($ctx, $args, $cond) = @_;
    my $cmtr = $ctx->stash('commenter');
    my $blog = $ctx->stash('blog');
    if ($cmtr && $blog && $cmtr->status($blog->id) == MT::Author::PENDING()) {
        return _hdlr_pass_tokens(@_);
    } else {
        return _hdlr_pass_tokens_else(@_);
    }
}

sub _hdlr_sub_cat_is_first {
    $_[0]->stash('subCatIsFirst');
}

sub _hdlr_sub_cat_is_last {
    $_[0]->stash('subCatIsLast');
}

sub _hdlr_sub_cats_recurse {
    my ($ctx, $args) = @_;
  
    # Make sure were in the right context
    # mostly to see if we have anything to actually build
    my $tokens = $ctx->stash('subCatTokens') 
        or return $ctx->error(MT->translate("MTSubCatsRecurse used outside of MTSubCategories"));
    my $builder = $ctx->stash('builder');
  
    my $cat = $ctx->stash('category');
  
    # Get the depth info
    my $max_depth = $args->{max_depth};
    my $depth = $ctx->stash('subCatsDepth') || 0;

    # Get the sorting info
    my $sort_method = $ctx->stash('subCatsSortMethod');
    my $sort_order  = $ctx->stash('subCatsSortOrder');

    # If we're too deep, return an emtry string because we're done
    return '' if ($max_depth && $depth >= $max_depth);
  
    my $cats = _sort_cats($ctx, $sort_method, $sort_order, $cat->children_categories)
        or return $ctx->error($ctx->errstr);

    # Init variables
    my $count = 0;
    my $res = '';

    # Loop through each immediate child, incrementing the depth by 1
    while (my $c = shift @$cats) {
        next if (!defined $c);
        local $ctx->{__stash}->{'category'} = $c;
        local $ctx->{__stash}->{'subCatIsFirst'} = !$count;
        local $ctx->{__stash}->{'subCatIsLast'} = !scalar @$cats;
        local $ctx->{__stash}->{'subCatsDepth'} = $depth + 1;

        local $ctx->{__stash}->{'entries'};
        local $ctx->{__stash}->{'category_count'};


        $ctx->{__stash}->{'entries'} = 
            lazy { my @args = ({ blog_id => $ctx->stash('blog_id'),
                                 status => MT::Entry::RELEASE() },
                               { 'join' => [ 'MT::Placement', 'entry_id',
                                             { category_id => $c->id } ],
                                 'sort' => 'created_on',
                                 direction => 'descend', });
              
                   my @entries = MT::Entry->load(@args); 
                   \@entries };
   
        defined (my $out = $builder->build($ctx, $tokens))
            or return $ctx->error($ctx->errstr);
   
        $res .= $out;
        $count++;
    }

    $res;
}

sub _hdlr_top_level_categories {
    my ($ctx, $args, $cond) = @_;

    # Unset the normaly hiding places for categories so
    # MTSubCategories doesn't pick them up
    local $ctx->{__stash}->{'category'} = undef;
    local $ctx->{__stash}->{'archive_category'} = undef;

    # Call MTSubCategories
    &_hdlr_sub_categories;
}

sub _hdlr_sub_categories {
    my ($ctx, $args, $cond) = @_;

    my $builder = $ctx->stash('builder');
    my $tokens  = $ctx->stash('tokens');

    # Do we want the current category?
    my $include_current = $args->{include_current};

    my $top = $args->{top};

    # Sorting information
    #   sort_order ::= 'ascend' | 'descend'
    #   sort_method ::= method name (e.g. package::method)
    #
    # sort_method takes precedence
    my $sort_order = $args->{sort_order} || 'ascend';
    my $sort_method = $args->{sort_method};

    # Store the tokens for recursion
    $ctx->stash('subCatTokens', $tokens);
  
    my $current_cat;
    my @cats;
  
    # If we find ourselves in a category context
    if (!$top && ($current_cat = $ctx->stash('category') || 
        $ctx->stash('archive_category'))) {

        if ($include_current) {
            # If we're to include it, just use it to seed the category list
            @cats = ($current_cat);
        } else {
            # Otherwise, use its children
            @cats = $current_cat->children_categories;
        }
    } else {
        # Otherwise, use the top level categories
        @cats = MT::Category->top_level_categories($ctx->stash('blog_id'));
    }
  
    my $cats = _sort_cats($ctx, $sort_method, $sort_order, @cats)
        or return $ctx->error($ctx->errstr);
 
    # Init variables
    my $count = 0;
    my $res = '';

    # Be sure the regular MT tags know we're in a category context
    local $ctx->{inside_mt_categories} = 1;

    local $ctx->{__stash}{'subCatsSortOrder'} = $sort_order;
    local $ctx->{__stash}{'subCatsSortMethod'} = $sort_method;

    # Loop through the immediate children (or the current cat,
    # depending on the arguments
    while (my $cat = shift @$cats) {
        next if (!defined $cat);
        local $ctx->{__stash}->{'category'} = $cat;
        local $ctx->{__stash}->{'subCatIsFirst'} = !$count;
        local $ctx->{__stash}->{'subCatIsLast'} = !scalar @$cats;

        local $ctx->{__stash}->{'entries'};
        local $ctx->{__stash}->{'category_count'};

        $ctx->{__stash}->{'entries'} = 
            lazy { my @args = ({ blog_id => $ctx->stash('blog_id'),
                                 status => MT::Entry::RELEASE() },
                               { 'join' => [ 'MT::Placement', 'entry_id',
                                             { category_id => $cat->id } ],
                                 'sort' => 'created_on',
                                 direction => 'descend', });
               
                   my @entries = MT::Entry->load(@args); 
                   \@entries };
    
        defined (my $out = $builder->build($ctx, $tokens, $cond))
            or return $ctx->error($ctx->errstr);

        $res .= $out;
        $count++;
    }

    $res;
}

sub _hdlr_parent_category {
    my ($ctx, $args, $cond) = @_;

    my $builder = $ctx->stash('builder');
    my $tokens  = $ctx->stash('tokens');

    # Get the current category
    defined (my $cat = _get_category_context($ctx))
        or return $ctx->error($ctx->errstr);
    return '' if ($cat eq '');
  
    # The category must have a parent, otherwise return empty string
    my $parent = $cat->parent_category or return '';

    # Setup the context and let 'er rip
    local $ctx->{__stash}->{category} = $parent;
    defined (my $out = $builder->build($ctx, $tokens, $cond))
        or return $ctx->error($ctx->errstr);

    $out;
}

sub _hdlr_parent_categories {
    my ($ctx, $args, $cond) = @_;

    my $builder = $ctx->stash('builder');
    my $tokens  = $ctx->stash('tokens');

    # Get the arguments
    my $exclude_current = $args->{'exclude_current'};
    my $glue = $args->{'glue'} || '';

    # Get the current category
    defined (my $cat = _get_category_context($ctx))
        or return $ctx->error($ctx->errstr);
    return '' if ($cat eq '');

    my @res;

    # Put together the list of parent categories
    # including the current one unless instructed otherwise
    my @cats = $cat->parent_categories;
    @cats = ($cat, @cats) unless ($exclude_current);
  
    # Start from the top and work our way down
    while (my $c = pop @cats) {
        local $ctx->{__stash}->{category} = $c;
        defined (my $out = $builder->build($ctx, $tokens, $cond))
            or return $ctx->error($ctx->errstr);
        if ($args->{sub_cats_path_hack} && $out !~ /\w/) {
            $out = 'cat-' . $c->id;
        }
        push @res, $out;
    }

    # Slap them all together with some glue
    return join $glue, @res;
}

sub _hdlr_top_level_parent {
    my ($ctx, $args, $cond) = @_;

    my $builder = $ctx->stash('builder');
    my $tokens  = $ctx->stash('tokens');

    # Get the current category
    defined (my $cat = _get_category_context($ctx))
        or return $ctx->error($ctx->errstr);
    return '' if ($cat eq '');

    my $out = "";

    # Get the list of parents
    my @parents = ($cat, $cat->parent_categories);

    # If there are any
    # Pop the top one of the list
    if (scalar @parents) {
        $cat = pop @parents;
        local $ctx->{__stash}->{category} = $cat;
        defined($out = $builder->build($ctx, $tokens, $cond))
            or return $ctx->error($ctx->errstr);
    }

    $out;
}

sub cat_path_to_category {
    my ($path, $blog_id) = @_;

    # The argument version always takes precedence
    # followed by the current category (i.e. MTCategories/MTSubCategories style)
    # then the current category for the archive
    # then undef
    my @cat_path = $path =~ m@(\[[^]]+\]|[^]/]+)@g;   # split on slashes, fields quoted by []
    @cat_path = map { $_ =~ s/^\[(.*)\]$/$1/; $_ } @cat_path;       # remove any []
    my $last_cat_id = 0;
    my $cat;
    for my $label (@cat_path) {
        $cat = MT::Category->load({ label => $label,
                                    parent => $last_cat_id,
                                    blog_id => $blog_id })
            or last;
        $last_cat_id = $cat->id;
    }
    if (!$cat && $path) {
        $cat = (MT::Category->load({ label => $path,
                                     blog_id => $blog_id }));
    }
    $cat;
}

sub _hdlr_entries_with_sub_categories {
    my ($ctx, $args, $cond) = @_;

    my $cat;
    if ($args->{category}) {
        $cat = cat_path_to_category($args->{category}, $ctx->stash('blog_id'));
    }
    $cat ||= $ctx->stash('category') 
         || $ctx->stash('archive_category') 
         || undef;

    my $save_entries = defined $ctx->stash('archive_category');
    my $saved_stash_entries;

    if (defined $cat) {
        my @kids = ($cat);

        my @cats = ();
        while (my $c = shift @kids) {
            push @cats, $c;
            push @kids, ($c->children_categories);
        }
      
        $args->{'category'} = ['OR', @cats];
        $saved_stash_entries = $ctx->{__stash}->{entries} if ($save_entries);
        delete $ctx->{__stash}->{'entries'};
    }

    my $res = _hdlr_entries($ctx, $args, $cond);
    $ctx->{__stash}->{entries} = $saved_stash_entries 
        if ($save_entries && $saved_stash_entries);
    $res;
}

sub _hdlr_sub_category_path {
    my ($ctx, $args, $cond) = @_;

    my $builder = $ctx->stash('builder');
    my $dir;
    if ($args->{separator}) {
        $dir = "dirify='$args->{separator}'";
    } else {
        $dir = "dirify='1'";
    }
    my $tokens  = $builder->compile($ctx, "<MTCategoryLabel $dir default=''>");
    # unfortunately, there's no way to apply a filter that would
    # take the output of the dirify step and, if it were blank,
    # use instead some other property of the category (such as the 
    # category ID). this hack tells parent_categories to do that
    # to the output of its contents.
    $args->{'sub_cats_path_hack'} = 1;

    $args->{'glue'} = '/';
    local $ctx->{__stash}->{tokens} = $tokens;
    &_hdlr_parent_categories;
}
  
sub _hdlr_has_sub_categories {
    my ($ctx, $args, $cond) = @_;

    # Get the current category context
    defined (my $cat = _get_category_context($ctx)) 
        or return $ctx->error($ctx->errstr);
    return if ($cat eq '');

    # Return the number of children for the category
    my @children = $cat->children_categories;
    scalar @children;
}

sub _hdlr_has_no_sub_categories {
    !&_hdlr_has_sub_categories;
}

sub _hdlr_has_parent_category {
    my ($ctx, $args) = @_;

    # Get the current category
    defined (my $cat = _get_category_context($ctx))
        or return $ctx->error($ctx->errstr);
    return if ($cat eq '');

    # Return the parent of the category
    return $cat->parent_category;
}

sub _hdlr_has_no_parent_category {
    return !&_hdlr_has_parent_category;
}

sub _hdlr_is_ancestor {
    my ($ctx, $args) = @_;

    # Get the current category
    defined (my $cat = _get_category_context($ctx)) or
        return $ctx->error($ctx->errstr);
    return if ($cat eq '');

    # Get the possible child category
    my $child = MT::Category->load({ label => $args->{'child'} }) || undef;
        return if (!defined $cat && !defined $child);

    return $cat->is_ancestor($child);
}

sub _hdlr_is_descendant {
    my ($ctx, $args) = @_;

    # Get the current category
    defined (my $cat = _get_category_context($ctx)) or
        return $ctx->error($ctx->errstr);
    return if ($cat eq '');

    # Get the possible parent category
    my $parent = MT::Category->load({ label => $args->{'parent'} }) || undef;
        return if (!defined $parent);

    return $cat->is_descendant($parent);
}

sub _get_category_context {
    my ($ctx) = @_;
  
    my $tag = $ctx->stash('tag');

    # Get our hands on the category for the current context
    # Either in MTCategories, a Category Archive Template
    # Or the category for the current entry
    my $cat = $ctx->stash('category') ||
        $ctx->stash('archive_category');

    if (!defined $cat) { 
    
        # No category found so far, test the entry
        if ($ctx->stash('entry')) {
            $cat = $ctx->stash('entry')->category;

            # Return empty string if entry has no category
            # as the tag has been used in the correct context
            # but there is no category to work with
            return '' if (!defined $cat);
        } else {
            return $ctx->error(MT->translate("MT[_1] must be used in a category context", $tag));
        }
    }
    return $cat;
}

sub _sort_cats {
    my ($ctx, $sort_method, $sort_order, @cats) = @_;

    # If sort_method is defined
    if (defined $sort_method) {
        my $package = $sort_method;

        # Check if it has a package name
        if ($package =~ /::/) {

            # Extract the package name
            $package =~ s/::[^(::)]+$//;

            # Make sure it's loaded
            eval (qq(use $package;));
            return $ctx->error(MT->translate("Cannot find sort_method")) if ($@);
        }

        # Sort the categories based on sort_method
        eval ("\@cats = sort $sort_method \@cats;");
        return $ctx->error(MT->translate("Error sorting categories: [_1]", $@)) if ($@);
    } else {
        if ($sort_order eq 'descend') {
            @cats = sort { $b->label cmp $a->label } @cats;
        } else {
            @cats = sort { $a->label cmp $b->label } @cats;
        }
    }

    return [ @cats ];
}

1;
