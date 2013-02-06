# Copyright 2001-2005 Six Apart. This code cannot be redistributed without
# permission from www.movabletype.org
#
# $Id: default.pm 466 2005-08-15 00:38:58Z hirata $

package MT::I18N::default;

use strict;
use MT::ConfigMgr;
use base qw( MT::ErrorHandler );

use constant DEFAULT_LENGTH_ENTRY_EXCERPT => 40;
use constant LENGTH_ENTRY_TITLE_FROM_TEXT => 5;
use constant LENGTH_ENTRY_PING_EXCERPT => 255;
use constant LENGTH_ENTRY_PING_TITLE_FROM_TEXT => 5;
use constant DISPLAY_LENGTH_MENU_TITLE => 22;
use constant DISPLAY_LENGTH_EDIT_COMMENT_TITLE => 25;
use constant DISPLAY_LENGTH_EDIT_COMMENT_AUTHOR => 25;
use constant DISPLAY_LENGTH_EDIT_COMMENT_TEXT_SHORT => 45;
use constant DISPLAY_LENGTH_EDIT_COMMENT_TEXT_LONG => 90;
use constant DISPLAY_LENGTH_EDIT_COMMENT_TEXT_BREAK_UP_SHORT => 30;
use constant DISPLAY_LENGTH_EDIT_COMMENT_TEXT_BREAK_UP_LONG => 80;
use constant DISPLAY_LENGTH_EDIT_PING_TITLE_FROM_EXCERPT => 12;
use constant DISPLAY_LENGTH_EDIT_PING_BREAK_UP => 30;
use constant DISPLAY_LENGTH_EDIT_ENTRY_TITLE => 22;
use constant DISPLAY_LENGTH_EDIT_ENTRY_TEXT_FROM_EXCERPT => 50;
use constant DISPLAY_LENGTH_EDIT_ENTRY_TEXT_BREAK_UP => 30;

sub guess_encoding {
    my $class = shift;
    my $enc = MT::ConfigMgr->instance->PublishCharset || 'utf-8';
    return $enc;
}

sub encode_text {
    my $class = shift;
    my ($text, $from, $to) = @_;
    return $text;
}

sub substr_text {
    my $class = shift;
    my ($text, $startpos, $length) = @_;
    return substr($text, $startpos, $length);
}

sub wrap_text {
    my $class = shift;
    my ($text, $col, $tab_init, $tab_sub) = @_;
    require Text::Wrap;
    $Text::Wrap::column = $col;
    $text = Text::Wrap::wrap($tab_init, $tab_sub, $text);
    return $text;
}

sub length_text {
    my $class = shift;
    my ($text) = @_;
    my $len = length($text);
    return $len;
}

sub first_n {
    # passthru first_n_words
    my $class = shift;
    my ($text, $length) = @_;
    $text = MT::Util::first_n_words($text, $length);
    return $text;
}

sub break_up_text {
    my $class = shift;
    my ($text, $length) = @_;
    $text =~ s/(\S{$length})/$1 /g;
    return $text;
}


my %HighASCII = (
    "\xc0" => 'A',    # A`
    "\xe0" => 'a',    # a`
    "\xc1" => 'A',    # A'
    "\xe1" => 'a',    # a'
    "\xc2" => 'A',    # A^
    "\xe2" => 'a',    # a^
    "\xc4" => 'Ae',   # A:
    "\xe4" => 'ae',   # a:
    "\xc3" => 'A',    # A~
    "\xe3" => 'a',    # a~
    "\xc8" => 'E',    # E`
    "\xe8" => 'e',    # e`
    "\xc9" => 'E',    # E'
    "\xe9" => 'e',    # e'
    "\xca" => 'E',    # E^
    "\xea" => 'e',    # e^
    "\xcb" => 'Ee',   # E:
    "\xeb" => 'ee',   # e:
    "\xcc" => 'I',    # I`
    "\xec" => 'i',    # i`
    "\xcd" => 'I',    # I'
    "\xed" => 'i',    # i'
    "\xce" => 'I',    # I^
    "\xee" => 'i',    # i^
    "\xcf" => 'Ie',   # I:
    "\xef" => 'ie',   # i:
    "\xd2" => 'O',    # O`
    "\xf2" => 'o',    # o`
    "\xd3" => 'O',    # O'
    "\xf3" => 'o',    # o'
    "\xd4" => 'O',    # O^
    "\xf4" => 'o',    # o^
    "\xd6" => 'Oe',   # O:
    "\xf6" => 'oe',   # o:
    "\xd5" => 'O',    # O~
    "\xf5" => 'o',    # o~
    "\xd8" => 'Oe',   # O/
    "\xf8" => 'oe',   # o/
    "\xd9" => 'U',    # U`
    "\xf9" => 'u',    # u`
    "\xda" => 'U',    # U'
    "\xfa" => 'u',    # u'
    "\xdb" => 'U',    # U^
    "\xfb" => 'u',    # u^
    "\xdc" => 'Ue',   # U:
    "\xfc" => 'ue',   # u:
    "\xc7" => 'C',    # ,C
    "\xe7" => 'c',    # ,c
    "\xd1" => 'N',    # N~
    "\xf1" => 'n',    # n~
    "\xdf" => 'ss',
);
my $HighASCIIRE = join '|', keys %HighASCII;

sub convert_high_ascii {
    my $class = shift;
    my($s) = @_;
    $s =~ s/($HighASCIIRE)/$HighASCII{$1}/g;
    return $s;
}

1;
