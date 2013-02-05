# Copyright 2001-2004 Six Apart. This code cannot be redistributed without
# permission from www.movabletype.org
#
# $Id: I18N.pm 477 2005-08-18 02:22:13Z hirata $

package MT::I18N;

use strict;
use MT;
use MT::ConfigMgr;

use MT::I18N::default;
use MT::I18N::en_us;
use MT::I18N::ja;

my %Supported_Language = map {$_ => 1} ( qw( en_us ja ) );

sub guess_encoding { _handle(guess_encoding => @_) }
sub encode_text { _handle(encode_text => @_) }
sub substr_text { _handle(substr_text => @_) }
sub wrap_text { _handle(wrap_text => @_) }
sub length_text { _handle(length_text => @_) }
sub first_n { _handle(first_n => @_) }
sub first_n_text { _handle(first_n => @_) } # for backward compatibility
sub break_up_text { _handle(break_up_text => @_) }
sub convert_high_ascii { _handle(convert_high_ascii => @_) }

sub const {
    my $label = shift;
    my $class = 'MT::I18N::' . _language();
    $class->$label();
}

sub _handle {
    my $meth = shift;
    my $lang = _language();
    my $class = 'MT::I18N::' . $lang;
    $class->$meth(@_);
}

sub _language {
    my $lang = lc MT::ConfigMgr->instance->DefaultLanguage;
    $Supported_Language{$lang} ? $lang : 'default';
}

1;
