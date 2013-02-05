package MT4i::Func;

########################################
# Sub Lenb_EUC - Ⱦ�ѥ��ʡ�3�Х��ȴޤ�EUCʸ������length
# ���������Х��ȿ��������ʸ����
# \x8E[\xA1-\xDF] = EUCȾ�ѥ�������ɽ��
# \x8F[\xA1-\xFE][\xA1-\xFE] = EUC3�Х���ʸ������ɽ��
# ���͡�Perl��⢪http://www.din.or.jp/~ohzaki/perl.htm
########################################

sub lenb_euc {
    my $llen;
    $llen = length($_[0]);                                        # ���̤�length
    $llen -= $_[0]=~s/(\x8E[\xA1-\xDF])/$1/g;                    # Ⱦ�ѥ��ʿ���ޥ��ʥ�
    $llen -= ($_[0]=~s/(\x8F[\xA1-\xFE][\xA1-\xFE])/$1/g)*2;    # 3�Х���ʸ����*2��ޥ��ʥ�
    return $llen;
}

########################################
# Sub Midb_EUC - Ⱦ�ѥ��ʡ�3�Х��ȴޤ�EUCʸ������substr
# ���������ڤ�Ф�����ʸ����
# ����������ڤ�Ф����ϰ��֡�0����
# �軰�������ڤ�Ф��Х��ȿ�
# \x8E[\xA1-\xDF] = EUCȾ�ѥ�������ɽ��
# \x8F[\xA1-\xFE][\xA1-\xFE] = EUC3�Х���ʸ������ɽ��
# ���͡�Perl��⢪http://www.din.or.jp/~ohzaki/perl.htm
########################################

sub midb_euc {
    my $llen1;
    my $llen2;
    my $lstr;
    my $lstart;

    # �褺���������ϰ��֤���ʤ���
    if ($_[1] == 0) {
        $lstart = 0;
    } else {
        $llen1 = $_[1];
        $lstr = substr($_[0], 0, $llen1);
        $llen2 = MT4i::Func::lenb_euc($lstr);
        my $llen3 = $llen1;
        while ($_[1] > $llen2) {
            $llen3 = $llen1;
            $llen3 += $lstr=~s/(\x8E[\xA1-\xDF])/$1/g;                    # Ⱦ�ѥ��ʿ���ץ饹
            $llen3 += ($lstr=~s/(\x8F[\xA1-\xFE][\xA1-\xFE])/$1/g)*2;    # 3�Х���ʸ����*2��ץ饹
            $lstr = substr($_[0], 0, $llen3);
            $llen2 = MT4i::Func::lenb_euc($lstr);
        }
        $llen1 = $llen3;

        # �Ǹ��ʸ�������ڤ�Ƥ��뤫Ƚ�ꤹ��
        if ($lstr =~ /\x8F$/ || $lstr =~ tr/\x8E\xA1-\xFE// % 2) {
            chop $lstr;
            $llen1--;
            if($lstr =~ /\x8F$/){
                $llen1--;
            }
        }
        $lstart = $llen1;
    }

    # ʸ������ڤ�Ф�
    $llen1 = $_[2];
    $lstr = substr($_[0], $lstart, $llen1);
    $llen2 = MT4i::Func::lenb_euc($lstr);
    my $llen3;
    while ($_[2] > $llen2) {
        $llen3 = $llen1;
        $llen3 += $lstr=~s/(\x8E[\xA1-\xDF])/$1/g;                    # Ⱦ�ѥ��ʿ���ץ饹
        $llen3 += ($lstr=~s/(\x8F[\xA1-\xFE][\xA1-\xFE])/$1/g)*2;    # 3�Х���ʸ����*2��ץ饹
        $lstr = substr($_[0], $lstart, $llen3);
        $llen2 = MT4i::Func::lenb_euc($lstr);
    }
    $llen1 = $llen3;

    # �Ǹ��ʸ�������ڤ�Ƥ��뤫Ƚ�ꤹ��
    if ($lstr =~ /\x8F$/ || $lstr =~ tr/\x8E\xA1-\xFE// % 2) {
        chop $lstr;
        if($lstr =~ /\x8F$/){
            chop $lstr;
        }
    }
    return $lstr;
}

########################################
# crypt()�ˤ��Ź沽���ȹ�
# ���͡�http://www.rfs.co.jp/sitebuilder/perl/05/01.html#crypt
########################################

# �Ź沽������ʸ����($val)�������ꡢ�Ź沽����ʸ������֤��ؿ�
sub enc_crypt {
    my ($val) = @_;

    my( $sec, $min, $hour, $day, $mon, $year, $weekday )
        = localtime( time );
    my( @token ) = ( '0'..'9', 'A'..'Z', 'a'..'z' );
    my $salt = $token[(time | $$) % scalar(@token)];
    $salt .= $token[($sec + $min*60 + $hour*60*60) % scalar(@token)];
    my $passwd2 =  crypt( $val, $salt );

    $passwd2 =~ s/\//\@2F/g;
    $passwd2 =~ s/\$/\@24/g;
    $passwd2 =~ s/\./\@2E/g;

    return $passwd2;
}

########################################
# �ѥ����($passwd1)�ȰŹ沽�����ѥ����($passwd2)�������ꡢ
# ���פ��뤫��Ƚ�ꤹ��ؿ�
########################################
sub check_crypt{
    my ($passwd1, $passwd2) = @_;

    $passwd2 =~ s/\@2F/\//g;
    $passwd2 =~ s/\@24/\$/g;
    $passwd2 =~ s/\@2E/\./g;

    # �Ź�Υ����å�
    if ( crypt($passwd1, $passwd2) eq $passwd2 ) {
        return 1;
    } else {
        return 0;
    }
}

############################################################
# calc_cache_size:���ӤΥ���å���(1���̤˽��ϤǤ��������)�����
# ���� ���ӤΥ���å��奵����
# ���͡�http://deneb.jp/Perl/mobile/
# Special Thanks��drry
############################################################
sub calc_cache_size {

    my ( $user_agent ) = @_;
    my $cache_size = 50*1024;
    if ( $user_agent =~ m|DoCoMo.*\W.*c(\d+).*(c\d+)?|i ) {
        $cache_size = $1*1024;
    } elsif ( $user_agent =~ m|DoCoMo|i ) {
        $cache_size = 5*1024;
    } elsif ( $user_agent =~ m!(?:SoftBank|Vodafone)/\d\.\d|MOT-\w980! ) {
        $cache_size = 300*1024;
    } elsif ( $user_agent =~ m!J-PHONE(?:/([45]\.\d))?! ) {
        $cache_size = ($1 ? ($1 >= 5.0 ? 200: ($1 >= 4.3 ? 30: 12)): 6)*1024;
    } elsif ( $ENV{HTTP_X_UP_DEVCAP_MAX_PDU} ) {
        $cache_size = $ENV{HTTP_X_UP_DEVCAP_MAX_PDU};
    } elsif ( $user_agent =~ m|KDDI\-| ) {
        $cache_size = 9*1024;
    } elsif ( $user_agent =~ m|UP\.Browser| ) {
        $cache_size = 7.5*1024;
    }
    return $cache_size;
}

#################################################################
# Sub Get_mt4ilink - MT4i�ؤΥ�󥯤����
#
# ������HTML���������MT4i�Ǳ�������Τ�Ŭ����������
# �������롣����Ū�ˤ� [rel|rev]="alternate" ��link�����Τ�����
# title="MT4i" ���뤤�� media="handheld" ��°�����ĥ����ǻ�
# �ꤵ��Ƥ��� href ���֤���ξ�����ä����� title="MT4i" ����
# ��ͥ�褹�롣���Ĥ���ʤ���ж�ʸ������֤���
#
#################################################################
sub get_mt4ilink {
    my $url = $_[0];

    require LWP::Simple;
    # ����襳��ƥ�ļ���
    my $content = LWP::Simple::get($url);
    if (!$content) {
        # ��������
        return "";
    }

    # �إå����μ��Ф�
    my $pattern = "<[\s\t]*?head[\s\t]*?>(.*?)<[\s\t]*?/[\s\t]*?head[\s\t]*?>";
    my @head = ($content =~ m/$pattern/is);
    if (!$head[0]) {
        return "";
    }

    # link�����μ��Ф�
    $pattern = "<[\s\t]*?link[\s\t]*?(.*?)[\s\t/]*?>";
    my @links = ($head[0] =~ m/$pattern/isg);

    my $mt4ilink = ""; # titile="MT4i"
    my $hhlink     = ""; # media="handheld"

    found : foreach my $link ( @links ) {
        my $title = "";
        my $rel = "";
        my $media = "";
        my $href = "";
        if ($link =~ /title[\s\t]*?=[\s\t]*?([^\s\t]*)/i) {
            $title = $1;
            $title =~ s/["']//g;
        }
        if ($link =~ /rel[\s\t]*?=[\s\t]*?([^\s\t]*)/i) {
            $rel = $1;
        } elsif ($link =~ /rev[\s\t]*?=[\s\t]*?([^\s\t]*)/i) {
            $rel = $1;
        }
        if ($rel) {
            $rel =~ s/["']//g;
        }
        if ($link =~ /media[\s\t]*?=[\s\t]*?([^\s\t]*)/i) {
            $media = $1;
            $media =~ s/["']//g;
        }
        if ($link =~ /href[\s\t]*?=[\s\t]*?([^\s\t]*)/i) {
            $href = $1;
            $href =~ s/["']//g;
        }
        if ((lc $rel) eq 'alternate') {
            if ((lc $title) eq 'mt4i') {
                $mt4ilink = $href;
                last found;
            } elsif ((lc $media) eq 'handheld') {
                if (!$hhlink) {
                    $hhlink = $href;
                }
            }
        }
    }

    if ($mt4ilink) {
        return $mt4ilink;
    }
    return $hhlink;
}

##################################################
# Sub Get_SubObjList - ���֥��ƥ��ꥪ�֥������ȥꥹ�Ȥμ���
##################################################
sub get_subcatobjlist {
    my $category = shift;
    
    #�����������ƥ��ꥪ�֥������Ȥ���ҥ��ƥ�������
    my @sub_categories = $category->children_categories;
    if (@sub_categories) {
        # ���֥��ƥ���μ���
        foreach my $sub_category (@sub_categories) {
            my @ssub_categories = &get_subcatobjlist($sub_category);
            foreach my $ssub_category (@ssub_categories) {
                push @sub_categories, $ssub_category;
            }
        }
    }
    return @sub_categories;
}

1;
