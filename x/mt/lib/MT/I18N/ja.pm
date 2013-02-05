# Copyright 2001-2005 Six Apart. This code cannot be redistributed without
# permission from www.movabletype.org
#
# $Id: I18N.pm 247 2004-10-19 03:43:40Z hirata $

package MT::I18N::ja;

use strict;
use MT::ConfigMgr;
use MT::Util qw(remove_html);
# use base qw( MT::I18N::default );

use constant DEFAULT_LENGTH_ENTRY_EXCERPT => 40;
use constant LENGTH_ENTRY_TITLE_FROM_TEXT => 10;
use constant LENGTH_ENTRY_PING_EXCERPT => 80;
use constant LENGTH_ENTRY_PING_TITLE_FROM_TEXT => 10;
use constant DISPLAY_LENGTH_MENU_TITLE => 11;
use constant DISPLAY_LENGTH_EDIT_COMMENT_TITLE => 12;
use constant DISPLAY_LENGTH_EDIT_COMMENT_AUTHOR => 12;
use constant DISPLAY_LENGTH_EDIT_COMMENT_TEXT_SHORT => 23;
use constant DISPLAY_LENGTH_EDIT_COMMENT_TEXT_LONG => 45;
use constant DISPLAY_LENGTH_EDIT_COMMENT_TEXT_BREAK_UP_SHORT => 30;
use constant DISPLAY_LENGTH_EDIT_COMMENT_TEXT_BREAK_UP_LONG => 80;
use constant DISPLAY_LENGTH_EDIT_PING_TITLE_FROM_EXCERPT => 25;
use constant DISPLAY_LENGTH_EDIT_PING_BREAK_UP => 30;
use constant DISPLAY_LENGTH_EDIT_ENTRY_TITLE => 11;
use constant DISPLAY_LENGTH_EDIT_ENTRY_TEXT_FROM_EXCERPT => 25;
use constant DISPLAY_LENGTH_EDIT_ENTRY_TEXT_BREAK_UP => 30;

use vars qw( $PKG );
my $PKG;

my $ENCODINGS_LABEL = {
    'shift_jis' => 'sjis',
    'iso-2022-jp' => 'jis',
    'euc-jp' => 'euc',
    'utf-8' => 'utf8',
    'ascii' => 'utf8',
    'iso-8859-1' => 'ascii',
};

my @ENCODINGS_ENCODE = (
    qw( euc-jp shiftjis 7bit-jis iso-2022-jp
        iso-2022-jp-1 jis0201-raw jis0208-raw
        jis0212-raw cp932 Macjapanese ));

use vars qw ( $AUTOLOAD );

sub AUTOLOAD {
    my $class = $_[0];
    $class->_load_module unless $PKG;
    my $meth = $AUTOLOAD;
    $meth =~ s/^.+:://g;

    # loop check
    my %supported_methods = map { $_ => 1 }
        qw( guess_encoding encode_text substr_text wrap_text
            length_text first_n first_n_text break_up_text 
            convert_high_ascii );
    return undef unless $supported_methods{$meth};

    $meth .= '_' . lc $PKG;
    no strict 'refs';
    *$AUTOLOAD = sub {
        shift;
        $class->$meth(@_);
    };
    goto &$AUTOLOAD;
}

sub guess_encoding_jcode {
    my $class = shift;
    my ($text) = @_;
    my $enc = Jcode::getcode($text);
    if (!$enc) {
	$enc = MT::ConfigMgr->instance->PublishCharset || 'utf-8';
    }
    if ($enc eq 'ascii') {
	$enc = 'utf-8';
    }
    if ($enc eq 'binary') {
	$enc = MT::ConfigMgr->instance->PublishCharset || 'utf-8';
    }
    $enc = $class->_conv_enc_label($enc);
    return $enc;
}

sub encode_text_jcode {
    my $class = shift;
    my ($text, $from, $to) = @_;
    if (!$from) {
        $from = $class->guess_encoding_jcode($text);
    }
    if (!$to) {
	$to = MT::ConfigMgr->instance->PublishCharset || 'utf-8';
    }
    $from = $class->_conv_enc_label($from);
    $to = $class->_conv_enc_label($to);
    return $text if ($from eq $to || $to eq 'ascii');
    return Jcode->new($text,$from)->$to();
}

sub substr_text_jcode {
    my $class = shift;
    my ($text, $startpos, $length, $enc) = @_;
    if ($length == 0) {
        $length = -1;
    }
    $enc = $class->_set_encode($text, $enc);
    my $euc_text = $class->encode_text($text,$enc,'euc-jp');
    my $out = '';
    my $c = 0;
    for (my $i=0;$i<length($euc_text);$i++) {
        last if ($length == 0);
        if ( substr($euc_text,$i,2) =~ /[\xA1-\xFE][\xA1-\xFE]/ ||
             substr($euc_text,$i,2) =~ /[\x8E][\xA1-\xDF]/) {
            if ($c >= $startpos && ($length-->0 || $length < 0)) {
                $out .= substr($euc_text,$i,2);
            }
            $c++;$i++;
            next;
        }
        if ( substr($euc_text,$i,3) =~ /[\x8F][\xA1-\xFE][\xA1-\xFE]/) {
            if ($c >= $startpos && ($length-->0 || $length < 0)) {
                $out .= substr($euc_text,$i,3);
            }
            $c++;$i+=2;
            next;
        }
        if ( ord(substr($euc_text,$i,1)) < 0x80 ) {
            if ($c >= $startpos && ($length-->0 || $length < 0)) {
                $out .= substr($euc_text,$i,1);
            }
            $c++;
            next;
        }
    }
    return $class->encode_text($out, 'euc-jp', $enc);
}

sub wrap_text_jcode {
    my $class = shift;
    my ($text, $cols, $tab_init, $tab_sub, $enc) = @_;
    $enc = $class->_set_encode($text, $enc);
    if (!$cols) {
        $cols = 72;
    }
    my $euc_text = $class->encode_text($text,$enc,'euc-jp');
    my $out = '';
    my $str = '';
    my $b = 0;
    for (my $i=0;$i<length($euc_text);$i++) {
        if ( substr($euc_text,$i,2) =~ /[\xA1-\xFE][\xA1-\xFE]/ ||
             substr($euc_text,$i,2) =~ /[\x8E][\xA1-\xDF]/) {
            $str = substr($euc_text,$i,2);
            $i++;
            $b+=2;
        }
        elsif ( substr($euc_text,$i,3) =~ /[\x8F][\xA1-\xFE][\xA1-\xFE]/) {
            $str = substr($euc_text,$i,3);
            $i+=2;
            $b+=2;
        }
        elsif ( substr($euc_text,$i,1) =~ /[\n\r]/ ) {
            $str = substr($euc_text,$i,1);
            $b = 0;
        }
        elsif ( ord(substr($euc_text,$i,1)) < 0x80 ) {
            $str = substr($euc_text,$i,1);
            $b+=1;
        }

        if ($b > $cols) {
            $out .= "\n";
            $b = 0;
        }
        $out .= $str;
    }
    return $class->encode_text($out,'euc-jp', $enc);
}

sub length_text_jcode {
    my $class = shift;
    my ($text, $enc) = @_;
    $enc = $class->_set_encode($text, $enc);

    my $euc_text= $class->encode_text($text, $enc, 'euc-jp');
    my $len = Jcode->new($euc_text, 'euc')->jlength();
    return $len;
}

sub first_n_jcode {
    my $class = shift;
    my ($text, $length, $enc) = @_;
    $enc = $class->_set_encode($text, $enc);

    my $euc_text = $class->encode_text($text, $enc, 'euc-jp');
    $euc_text = MT::Util::remove_html($euc_text);
    $euc_text =~ s/(\r?\n)+/ /g;
    my $out = $class->substr_text_jcode($euc_text, 0, $length, 'euc-jp');
    return $class->encode_text($out,'euc-jp', $enc);
}

sub break_up_text_jcode {
    my $class = shift;
    my ($text, $cols, $enc) = @_;
    return $text;
}

sub guess_encoding_encode {
    my $class = shift;
    my ($text) = @_;
    Encode::Guess->set_suspects(@ENCODINGS_ENCODE);
    my $dec = Encode::Guess->guess($text);
    if (ref($dec)) {
        return $dec->name;
    } else {
	for my $encode_name ( @ENCODINGS_ENCODE ) {
	    Encode::Guess->set_suspects($encode_name);
	      $dec = Encode::Guess->guess($text);
	      if (ref($dec)) {
		  return $dec->name;
	      }
	  }
        return 'utf-8';
    }
}

sub encode_text_encode {
    my $class = shift;
    my($text, $from, $to) = @_;
    if (!$from) {
        $from = $class->guess_encoding_encode($text);
    }
    $from = 'euc-jp' if ($from eq 'euc');
    if (!$to) {
	$to = MT::ConfigMgr->instance->PublishCharset || 'utf-8';
    }
    $to = 'euc-jp' if ($to eq 'euc');

    if ($from ne $to) {
        Encode::_utf8_off($text);
        eval { Encode::from_to($text, $from, $to); };
        if (my $err = $@) {
            warn $err;
        }
    }

    Encode::_utf8_off($text);
    $text;
}

sub substr_text_encode {
    my $class = shift;
    my ($text, $startpos, $length, $enc) = @_;
    $enc = $class->_set_encode($text, $enc);

    $text = $class->_conv_to_utf8($text, $enc);
    Encode::_utf8_on($text);
    $text = substr($text, $startpos, $length);
    Encode::_utf8_off($text);
    $text = $class->_conv_from_utf8($text, $enc);
    $text;
}

sub wrap_text_encode {
    my $class = shift;
    my ($text, $cols, $tab_init, $tab_sub, $enc) = @_;
    $text = $class->wrap_text_jcode($text, $cols, $tab_init, $tab_sub, $enc);
    $text;
}

sub length_text_encode {
    my $class = shift;
    my ($text, $enc) = @_;
    $enc = $class->_set_encode($text, $enc);

    $text = $class->_conv_to_utf8($text, $enc);
    Encode::_utf8_on($text);
    my $len = length($text);
    Encode::_utf8_off($text);
    return $len;
}

sub first_n_encode {
    my $class = shift;
    my ($text, $length, $enc) = @_;
    $enc = $class->_set_encode($text, $enc);
    $text = $class->_conv_to_utf8($text, $enc);
    $text = MT::Util::remove_html($text);
    $text =~ s/(\r?\n)+/ /g;
    $text = $class->substr_text_encode($text, 0, $length, 'utf-8');
    $text = $class->_conv_from_utf8($text, $enc);
    return $text;
}

sub break_up_text_encode {
    my $class = shift;
    my ($text, $cols, $enc) = @_;
    return $text;
}

sub _set_encode {
    my $class = shift;
    my ($text, $enc) = @_;

    if (defined($enc)) {
        unless ($enc) {
            my $meth = 'guess_encodeing_' . lc $PKG;
            $enc = $class->$meth($text);
        }
    } else {
        $enc = MT::ConfigMgr->instance->PublishCharset || 'utf-8';
    }
    return $enc;
}

sub _conv_enc_label {
    my $class = shift;
    my $enc = shift;
    $enc = lc $enc;
    $enc = $ENCODINGS_LABEL->{$enc} ? $ENCODINGS_LABEL->{$enc} : $enc;
    return $enc;
}

sub _conv_to_utf8 {
    my $class = shift;
    my ($text, $enc) = @_;
    return $text if lc($enc) eq 'utf-8';
    $class->encode_text_encode($text, $enc, 'utf-8');
}

sub _conv_from_utf8 {
    my $class = shift;
    my ($text, $enc) = @_;
    return $text if lc($enc) eq 'utf-8';
    $class->encode_text_encode($text, 'utf-8', $enc );
}

sub _load_module {
    my $class = shift;
    return $PKG if $PKG;
    my $use_jcode = MT::ConfigMgr->instance->UseJcodeModule ? 1 : 0;
    if ($] > 5.008 && !$use_jcode) {
        eval "require Encode;";
        unless ($@) {
            $PKG = 'Encode';
            require Encode::Guess;
            return $PKG;
        }
    } else {
        eval "require Jcode;";
        unless ($@) {
            $PKG = 'Jcode';
            return $PKG;
        }
    }
    return undef;
}

sub convert_high_ascii_jcode {
    my $class = shift;
    my ($s) = @_;
    $s = $class->encode_text_jcode($s, undef, 'utf-8');
    $s;
}

sub convert_high_ascii_encode {
    my $class = shift;
    my ($s) = @_;
    $s = $class->encode_text_encode($s, undef, 'utf-8');
    $s;
}

1;
