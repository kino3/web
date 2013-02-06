# Copyright 2001-2005 Six Apart. This code cannot be redistributed without
# permission from www.sixapart.com.  For more information, consult your
# Movable Type license.
#
# $Id: Comment.pm 16546 2005-08-23 04:57:57Z bchoate $

package MT::Comment;
use strict;

use MT::Object;
@MT::Comment::ISA = qw( MT::Object );
__PACKAGE__->install_properties({
    column_defs => {
        'id' => 'integer not null auto_increment',
        'blog_id' => 'integer not null',
        'entry_id' => 'integer not null',
        'author' => 'string(100)',
        'commenter_id' => 'integer',
        'visible' => 'boolean',
        'junk_status' => 'smallint',
        'email' => 'string(75)',
        'url' => 'string(255)',
        'text' => 'text',
        'ip' => 'string(16)',
        'last_moved_on' => 'datetime not null',
        'junk_score' => 'float',
        'junk_log' => 'text',
    },
    indexes => {
        ip => 1,
        created_on => 1,
        entry_id => 1,
        blog_id => 1,
        email => 1,
        commenter_id => 1,
        visible => 1,
        junk_status => 1,
        last_moved_on => 1,
        junk_score => 1,
    },
    defaults => {
        junk_status => 0,
        last_moved_on => '20000101000000',
    },
    audit => 1,
    datasource => 'comment',
    primary_key => 'id',
});

use constant JUNK => -1;
use constant NOT_JUNK => 1;

my %blocklists = ();

sub is_junk {
    $_[0]->junk_status == JUNK;
}

sub is_not_junk {
    $_[0]->junk_status != JUNK;
}

sub is_not_blocked { 
    my ($eh, $cmt) = @_;
    
    my($host, @hosts);
    # other URI schemes?
    require MT::Util;
    @hosts = MT::Util::extract_urls($cmt->text);
    
    my $not_blocked = 1;
    my $blog_id = $cmt->blog_id;
    if (!$blocklists{$blog_id}) {
        require MT::Blocklist;
        my @blocks = MT::Blocklist->load( { blog_id => $blog_id } );
        $blocklists{$blog_id} = [ @blocks ];
    }
    if (@{$blocklists{$blog_id}}) {
        for my $h (@hosts) {
            for my $b (@{$blocklists{$blog_id}}) {
                $not_blocked = 0 if ($h eq $b->text);
            }
        }
    }
    $not_blocked;
}

sub next {
    my $comment = shift;
    my($publish_only) = @_;
    $publish_only = $publish_only ? {'visible' => 1} : {};
    $comment->_nextprev('next', $publish_only);
}

sub previous {
    my $comment = shift;
    my($publish_only) = @_;
    $publish_only = $publish_only ? {'visible' => 1} : {};
    $comment->_nextprev('previous', $publish_only);
}

sub _nextprev {
    my $obj = shift;
    my $class = ref($obj);
    my ($direction, $publish_only) = @_;
    return undef unless ($direction eq 'next' || $direction eq 'previous');
    my $label = '__' . $direction;
    $direction = $direction eq 'next' ? 'ascend' : 'descend';

    unless ($obj->{$label} || !$obj->created_on) {
        $obj->{$label} = $class->load({
            blog_id => $obj->blog_id,
            created_on => $obj->created_on,
            %{$publish_only},
        },{
            'sort' => 'id',
            direction => $direction,
            start_val => $obj->id,
            limit => 1,
        });
        unless ($obj->{$label}) {
            my $o = $class->load( {
                blog_id => $obj->blog_id,
                %{$publish_only},
            }, {
                limit => 1,
                'sort' => 'created_on',
                direction => $direction,
                start_val => $obj->created_on,
            });
            $obj->{$label} = $class->load({
                blog_id => $obj->blog_id,
                created_on => $o->created_on,
                %{$publish_only},
            }, {
                limit => 1,
                'sort' => 'id',
                direction => $direction,
            }) if $o;
        }
    }
    $obj->{$label};
}

sub entry {
    my ($comment) = @_;
    my $entry = $comment->{__entry};
    unless ($entry) {
        my $entry_id = $comment->entry_id;
        return undef unless $entry_id;
        require MT::Entry;
        $entry = MT::Entry->load($entry_id) or
            return $comment->error(MT->translate(
		"Load of entry '[_1]' failed: [_2]", $entry_id, MT::Entry->errstr));
        $comment->{__entry} = $entry;
    }
    return $entry;
}

sub blog {
    my ($comment) = @_;
    my $blog = $comment->{__blog};
    unless ($blog) {
        my $blog_id = $comment->blog_id;
        require MT::Blog;
        $blog = MT::Blog->load($blog_id) or
            return $comment->error(MT->translate(
		"Load of blog '[_1]' failed: [_2]", $blog_id, MT::Blog->errstr));
        $comment->{__blog} = $blog;
    }
    return $blog;
}

sub junk {
    my ($comment) = @_;
    if (($comment->junk_status || 0) != JUNK) {
        require MT::Util;
        my @ts = MT::Util::offset_time_list(time, $comment->blog_id);
        my $ts = sprintf("%04d%02d%02d%02d%02d%02d",
                         $ts[5]+1900, $ts[4]+1, @ts[3,2,1,0]);
        $comment->last_moved_on($ts);
    }
    $comment->junk_status(JUNK);
    $comment->visible(0);
}

sub moderate {
    my ($comment) = @_;
    $comment->visible(0);
}

sub approve {
    my ($comment) = @_;
    $comment->visible(1);
    $comment->junk_status(NOT_JUNK);
}

*publish = \&approve;

sub all_text {
    my $this = shift;
    my $text = $this->column('author') || '';
    $text .= "\n" . ($this->column('email') || '');
    $text .= "\n" . ($this->column('url') || '');
    $text .= "\n" . ($this->column('text') || '');
    $text;
}

sub is_published {
    return $_[0]->visible && !$_[0]->is_junk;
}

sub is_moderated {
    return !$_[0]->visible() && !$_[0]->is_junk();
}

sub log {
    # TBD: pre-load __junk_log when loading the comment
    my $comment = shift;
    push @{$comment->{__junk_log}}, @_;
}

sub save {
    my $comment = shift;
    $comment->junk_log(join "\n", @{$comment->{__junk_log}})
        if ref $comment->{__junk_log} eq 'ARRAY';
    $comment->SUPER::save();
}

1;
__END__

=head1 NAME

MT::Comment - Movable Type comment record

=head1 SYNOPSIS

    use MT::Comment;
    my $comment = MT::Comment->new;
    $comment->blog_id($entry->blog_id);
    $comment->entry_id($entry->id);
    $comment->author('Foo');
    $comment->text('This is a comment.');
    $comment->save
        or die $comment->errstr;

=head1 DESCRIPTION

An I<MT::Comment> object represents a comment in the Movable Type system. It
contains all of the metadata about the comment (author name, email address,
homepage URL, IP address, etc.), as well as the actual body of the comment.

=head1 USAGE

As a subclass of I<MT::Object>, I<MT::Comment> inherits all of the
data-management and -storage methods from that class; thus you should look
at the I<MT::Object> documentation for details about creating a new object,
loading an existing object, saving an object, etc.

=head1 DATA ACCESS METHODS

The I<MT::Comment> object holds the following pieces of data. These fields can
be accessed and set using the standard data access methods described in the
I<MT::Object> documentation.

=over 4

=item * id

The numeric ID of the comment.

=item * blog_id

The numeric ID of the blog in which the comment is found.

=item * entry_id

The numeric ID of the entry on which the comment has been made.

=item * author

The name of the author of the comment.

=item * commenter_id

The author_id for the commenter; this will only be defined if the
commenter is registered, which is only required if the blog config
option allow_unreg_comments is false.

=item * ip

The IP address of the author of the comment.

=item * email

The email address of the author of the comment.

=item * url

The URL of the author of the comment.

=item * text

The body of the comment.

=item * visible

Returns a true value if the comment should be displayed. Comments can
be hidden if comment registration is required and the commenter is
pending approval.

=item * created_on

The timestamp denoting when the comment record was created, in the format
C<YYYYMMDDHHMMSS>. Note that the timestamp has already been adjusted for the
selected timezone.

=item * modified_on

The timestamp denoting when the comment record was last modified, in the
format C<YYYYMMDDHHMMSS>. Note that the timestamp has already been adjusted
for the selected timezone.

=back

=head1 DATA LOOKUP

In addition to numeric ID lookup, you can look up or sort records by any
combination of the following fields. See the I<load> documentation in
I<MT::Object> for more information.

=over 4

=item * created_on

=item * entry_id

=item * blog_id

=back

=head1 AUTHOR & COPYRIGHTS

Please see the I<MT> manpage for author, copyright, and license information.

=cut
