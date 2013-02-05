#!/usr/bin/perl
##################################################
#
# MovableType�� i-mode�Ѵ�������ץ�
# ��MT4i��
my $version = "2.25";
# Copyright (C) ��Ŵ All rights reserved.
# Special Thanks
#           �����ꥦ���˼� & Tonkey & drry
#
# MT4i - t2o2-Wiki
#  ��http://www.hazama.nu/pukiwiki/index.php?MT4i
# Tonkey�����Tonkey Magic
#  ��http://tonkey.mails.ne.jp/
# �����ꥦ���˼ߤο����¤�Ȥ
#  ��http://mayoi.net/
# drry�����drry+@->Weblog
#  ��http://blog.drry.jp/
#
# -- �������������� --
# �֤ä��㤱���Ԥ�������Фä���Ρ�ư���Ф�����פ�
# �����ǥ��󥰤��Ƥޤ�����Perl�˴ؤ��Ƥ��ǿ�Ʊ���ʤΤǡ�
# ������������������Ū��̤�Ϥ����Ϥ��ƼϤ���������
# -- �����������ޤ� --
#
##################################################

use strict;
use CGI;

# �����ե�������ɤ߹���
eval {require 'mt4ilib/Config.pl'; 1} || die print "Content-type: text/plain; charset=EUC-JP\n\n\"./mt4ilib/Config.pl\"�����դ���ޤ���";
eval {require 'mt4ilib/Func.pl'; 1} || die print "Content-type: text/plain; charset=EUC-JP\n\n\"./mt4ilib/Func.pl\"�����դ���ޤ���";

# �����ɤ߹���
my %cfg = Config::Read("./mt4icfg.cgi");

unshift @INC, $cfg{MT_DIR} . 'lib';
unshift @INC, $cfg{MT_DIR} . 'extlib';

####################
# HTML::Entities ��̵ͭĴ��
my $hentities;
eval 'use HTML::Entities;';
if($@){
    $hentities = 0;
}else{
    $hentities = 1;
}

####################
# Jcode.pm��̵ͭĴ��
eval 'use Jcode;';
if($@){
    print "Content-type: text/plain; charset=EUC-JP\n\n\"Jcode.pm\"�����󥹥ȡ��뤵��Ƥ��ޤ���";
    exit;
}

####################
# User Agent �ˤ�륭��ꥢȽ��
# ���͡�http://specters.net/cgipon/labo/c_dist.html
my $ua;
my @user_agent = split(/\//,$ENV{'HTTP_USER_AGENT'});
my $png_flag;
if ($user_agent[0] eq 'ASTEL') {
    # �ɥå�i �Ѥν���
    $ua = 'other';
} elsif ($user_agent[0] eq 'UP.Browser') {
    # EZweb ��ü���Ѥν���
    $ua = 'ezweb';
} elsif ($user_agent[0] =~ /^KDDI/) {
    # EZweb WAP2.0 �б�ü���Ѥν���
    $ua = 'ezweb';
} elsif ($user_agent[0] eq 'PDXGW') {
    # H" �Ѥν���
    $ua = 'other';
} elsif ($user_agent[0] eq 'DoCoMo') {
    # i-mode �Ѥν���
    $ua = 'i-mode';
} elsif ($user_agent[0] eq 'Vodafone' ||
         $user_agent[0] eq 'SoftBank') {
    # J-SKY �Ѥν���
    $ua = 'j-sky';
} elsif ($user_agent[0] eq 'J-PHONE') {
    # J-SKY �Ѥν���
    $ua = 'j-sky';
    
    # PNG����ɽ���Ǥ��ʤ�����Ϥ�������ʤΤǻ����˥����å�����
    if (($user_agent[2] =~ /^J-DN02/) ||
        ($user_agent[2] =~ /^J-P02/) ||
        ($user_agent[2] =~ /^J-P03/) ||
        ($user_agent[2] =~ /^J-T04/) ||
        ($user_agent[2] =~ /^J-SA02/) ||
        ($user_agent[2] =~ /^J-SH02/) ||
        ($user_agent[2] =~ /^J-SH03/)){
            $png_flag = 1;
    }
} elsif ($user_agent[1] =~ 'DDIPOCKET') {
    # AirH"PHONE�Ѥν���
    $ua = 'i-mode';
} elsif ($user_agent[0] eq 'L-mode') {
    # L-mode �Ѥν���
    $ua = 'other';
} else {
    # ����ʳ�
    $ua = 'other';
}

####################
# AccessKey��ʸ��������
my @nostr;
my @akstr;
for (my $i = 0; $i <= 9; $i++)  {
    $nostr[$i] = "";
    $akstr[$i] = "";
}
my $mt4ilinkstr = $cfg{Ainori_Str_o};
my $ExitChtmlTransStr = $cfg{ECTrans_Str_o};
if ($cfg{AccessKey} eq "yes") {
    if ($ua eq "i-mode" || $ua eq "ezweb") {
    # i-mode �ڤ� EZweb
        $mt4ilinkstr = $cfg{Ainori_Str_i};
        $ExitChtmlTransStr = $cfg{ECTrans_Str_i};
        for (my $i = 1; $i <= 10; $i++) {
            if ($i < 10) {
                my $code = 63878 + $i;
                $nostr[$i] = "&#$code;";
                $akstr[$i] = ", accesskey=\"$i\"";
            } else {
                $nostr[0] = "&#63888;";
                $akstr[0] = ", accesskey=\"0\"";
            }
        }
    } elsif ($ua eq "j-sky") {
        # J-SKY
        $mt4ilinkstr = $cfg{Ainori_Str_j};
        $ExitChtmlTransStr = $cfg{ECTrans_Str_j};
        $nostr[1] = "\x1B\$F<\x0F";
        $nostr[2] = "\x1B\$F=\x0F";
        $nostr[3] = "\x1B\$F>\x0F";
        $nostr[4] = "\x1B\$F?\x0F";
        $nostr[5] = "\x1B\$F@\x0F";
        $nostr[6] = "\x1B\$FA\x0F";
        $nostr[7] = "\x1B\$FB\x0F";
        $nostr[8] = "\x1B\$FC\x0F";
        $nostr[9] = "\x1B\$FD\x0F";
        $nostr[0] = "\x1B\$FE\x0F";
        for (my $i = 1; $i <= 10; $i++) {
            if ($i < 10) {
                $akstr[$i] = ", directkey=\"$i\" nonumber";
            } else {
                $akstr[0] = ", directkey=\"0\" nonumber";
            }
        }
    }
}

####################
# �����μ���
my $q = new CGI();

if (!$cfg{Blog_ID}) {
    $cfg{Blog_ID} = $q->param("id");    # blog ID
}
my $mode = $q->param("mode");            # �����⡼��
my $no = $q->param("no");                # ����ȥ꡼NO
my $eid = $q->param("eid");                # ����ȥ꡼ID
my $ref_eid = $q->param("ref_eid");        # �������Υ���ȥ꡼ID
my $page = $q->param("page");            # �ڡ���NO
my $sprtpage = $q->param("sprtpage");    # ʬ��ڡ�����
my $sprtbyte = $q->param("sprtbyte");    # �ڡ���ʬ��byte��
my $redirect_url = $q->param("url");    # ������쥯�����URL
my $img = $q->param("img");                # ������URL
my $cat = $q->param("cat");                # ���ƥ���ID
my $post_from = $q->param("from");        # ��Ƽ�
my $post_mail = $q->param("mail");        # �᡼��
my $post_text = $q->param("text");        # ������

my $pw_text = $q->param("pw_text");        # �Ź沽�ѥ����
my $key = $q->param("key");                # �Ź沽����
my $entry_cat = $q->param("entry_cat");                    # ����ȥ꡼�Υ��ƥ��꡼
my $entry_title = $q->param("entry_title");                # ����ȥ꡼�Υ����ȥ�
my $entry_text = $q->param("entry_text");                # ����ȥ꡼������
my $entry_text_more = $q->param("entry_text_more");        # ����ȥ꡼���ɵ�
my $entry_excerpt = $q->param("entry_excerpt");            # ����ȥ꡼�γ���
my $entry_keywords = $q->param("entry_keywords");        # ����ȥ꡼�Υ������
my $entry_tags = $q->param("entry_tags");                # ����ȥ꡼�Υ���
my $post_status = $q->param("post_status");                # ����ȥ꡼�Υ��ơ�����
my $post_status_old = $q->param("post_status_old");        # ����ȥ꡼���Խ����Υ��ơ�����
my $allow_comments = $q->param("allow_comments");        # ����ȥ꡼�Υ����ȵ��ĥ����å�
my $allow_pings = $q->param("allow_pings");                # ����ȥ꡼��ping���ĥ����å�
my $text_format = $q->param("convert_breaks");            # ����ȥ꡼�Υƥ����ȥե����ޥå�
my $entry_created_on = $q->param("entry_created_on");    # ����ȥ꡼�κ�������
my $entry_authored_on = $q->param("entry_authored_on");    # ����ȥ꡼�θ�������

# PerlMagick ��̵ͭĴ��
my $imk = 0;
if ($mode eq 'image' || $mode eq 'img_cut') {
    eval 'use Image::Magick;';

    if ($cfg{ImageAutoReduce} eq "imagemagick") {
        if($@){
            $imk = 0;
        }else{
            $imk = 1;
        }
    } else {
        $imk = 0;
    }
} elsif ($cfg{ImageAutoReduce} eq "picto") {
    $imk = 2;
}

my $data;    # ɽ��ʸ�����Ѥ��ѿ����������

#�������ѰŹ沽����������å�
my $admin_mode;
if (($key ne "")&&(MT4i::Func::check_crypt($cfg{AdminPassword}.$cfg{Blog_ID},$key))){
    $admin_mode = 'yes';
}else{
    $admin_mode = 'no';
    $key = "";
}

####################
# mt.cfg���ɤ߹���
eval{ require MT; };
if($@){
    $data .= "<p>MT.pm�����դ���ޤ���<br>";
    $data .= "MT�ۡ���ǥ��쥯�ȥ�������ľ���Ƥ���������</p>";
    $data .= $@;
    &errorout;
    exit;      # exit����
}
my $mt;
if (-e $cfg{MT_DIR} . 'mt-config.cgi') {
    $mt = MT->new( Config => $cfg{MT_DIR} . 'mt-config.cgi', Directory => $cfg{MT_DIR} )
        or die print "Content-type: text/plain;\n\n".MT->errstr;
} else {
    $mt = MT->new( Config => $cfg{MT_DIR} . 'mt.cfg', Directory => $cfg{MT_DIR} )
        or die print "Content-type: text/plain;\n\n".MT->errstr;
}

####################
# Encode.pm��̵ͭĴ��
my $ecd;
eval 'use Encode;';
if($@){
    $ecd = 0;
}else{
    eval 'use Encode::JP::H2Z;';
    $ecd = 1;
}

####################
# blog ID�����ꤵ��Ƥ��ʤ��ä����ϥ��顼
if (!$cfg{Blog_ID}) {
    $data = "Error��������blog ID����ꤷ�Ƥ���������<br>";
    # blog����ɽ��
    $data .= "<br>";
    require MT::Blog;
    my @blogs = MT::Blog->load(undef,
                            {unique => 1});

    # ������
    @blogs = sort {$a->id <=> $b->id} @blogs;
    
    $data .= '<table border="1">';
    $data .= '<tr><th style="color:#FF0000;">blog ID</th><th>blog Name</th><th>Description</th></tr>';
    
    # ɽ��
    for my $blog (@blogs) {
        my $blog_id = $blog->id;
        my $blog_name = &conv_euc_z2h($blog->name);
        my $blog_description = &conv_euc_z2h($blog->description);
        $data .= "<tr><th style=\"color:#FF0000;\">$blog_id</th><td><a href=\"./$cfg{MyName}?id=$blog_id\">$blog_name</a></td><td>$blog_description</td></tr>";
    }

    $data .= '</table><br><span style="font-weight:bold;">blog ID �λ�����ˡ��</span><br>��MT4i.cgi ������ˤ� "<span style="font-weight:bold;">$blog_id</span>" �˾嵭 <span style="color:#FF0000;font-weight:bold;">blog ID</span> ����ꤹ�뤫��<br>���⤷���Ͼ嵭 <span style="color:#FF0000;font-weight:bold;">blog Name</span> �ˎ؎ݎ�����Ƥ��� URL �ǎ����������롣';
    
    &errorout;
    exit;      # exit����
}

####################
# PublishCharset�μ���
my $conv_in = lc $mt->{cfg}->PublishCharset eq lc "Shift_JIS"   ? "sjis"
            : lc $mt->{cfg}->PublishCharset eq lc "ISO-2022-JP" ? "jis"
            : lc $mt->{cfg}->PublishCharset eq lc "UTF-8"       ? "utf8"
            : lc $mt->{cfg}->PublishCharset eq lc "EUC-JP"      ? "euc"
            : "utf8";

####################
# blog̾�ڤӳ��פμ���
require MT::Blog;
my $blog = MT::Blog->load($cfg{Blog_ID},
                      {unique => 1});

# ������blog ID
if (!$blog) {
    if ($hentities == 1) {
        $data = 'ID \''.encode_entities($cfg{Blog_ID}).'\' ��blog��¸�ߤ��ޤ���';
    } else {
        $data = 'ID \''.$cfg{Blog_ID}.'\' ��blog��¸�ߤ��ޤ���';
    }
    &errorout;
    exit;      # exit����
}

# blog̾�����ס������ȴ�Ϣ������ѿ��˳�Ǽ
my $blog_name = &conv_euc_z2h($blog->name);
my $description = &conv_euc_z2h($blog->description);
my $sort_order_comments = $blog->sort_order_comments;
my $email_new_comments = $blog->email_new_comments;
my $email_new_pings = $blog->email_new_pings;
my $convert_paras = $blog->convert_paras;
my $convert_paras_comments = $blog->convert_paras_comments;

####################
# ����$mode��Ƚ��
if (!$mode)                        { &main }
if ($mode eq 'individual')        { &individual }
if ($mode eq 'individual_rcm')    { &individual }
if ($mode eq 'individual_lnk')    { &individual }
if ($mode eq 'ainori')            { &individual }
if ($mode eq 'comment')            { &comment }
if ($mode eq 'comment_rcm')        { &comment }
if ($mode eq 'comment_lnk')        { &comment }
if ($mode eq 'image')            { &image }
if ($mode eq 'img_cut')            { &image_cut }
if ($mode eq 'postform')        { &postform }
if ($mode eq 'postform_rcm')    { &postform }
if ($mode eq 'postform_lnk')    { &postform }
if ($mode eq 'post')            { &post }
if ($mode eq 'post_rcm')        { &post }
if ($mode eq 'post_lnk')        { &post }
if ($mode eq 'recentcomment')    { &recent_comment }
if ($mode eq 'trackback')        { &trackback }
if ($mode eq 'redirect')        { &redirector }


# �������ѥХå��ɥ���ɽ��
if ($cfg{AdminDoor} eq "yes"){
    if ($mode eq 'admindoor')    { &admindoor }
}

#--- ����������ϴ����⡼�ɤǤ����¹ԤǤ��ʤ� ---

    if ($admin_mode eq "yes") {
        if ($mode eq 'entryform')                { &entryform }
        if ($mode eq 'entry')                    { &entry }
        if ($mode eq 'comment_del')                { &comment_del }
        if ($mode eq 'entry_del')                  { &entry_del }
        if ($mode eq 'trackback_del')            { &trackback_del }
        if ($mode eq 'trackback_ipban')            { &trackback_ipban }
        if ($mode eq 'comment_ipban')            { &comment_ipban }
        if ($mode eq 'email_comments')            { &email_comments }
        
        if ($mode eq 'confirm_comment_del')        { &confirm }
        if ($mode eq 'confirm_entry_del')        { &confirm }
        if ($mode eq 'confirm_trackback_del')    { &confirm }
    }

########################################
# Sub Main - �ȥåץڡ���������
########################################

sub main {
    if(!$mode && !$page) { $page = 0 }
    if ($cfg{AccessKey} eq "yes" && ($ua eq "i-mode" || $ua eq "j-sky" || $ua eq "ezweb")) {
        # �������ä���Υ����������ĥ�����������ͭ���ξ���$cfg{DispNum}��6�ʲ��ˤ���
        if ($cfg{DispNum} > 6) {
            $cfg{DispNum} = 6;
        }
    }
    my $rowid;
    if($page == 0) { $rowid = 0 } else { $rowid = $page * $cfg{DispNum} }
    
    ####################
    # �����μ���
    my $ttlcnt = &get_ttlcnt;
    
    ####################
    # �����μ���
    my @entries = &get_entries($rowid, $cfg{DispNum});
    
    # �������������$cfg{DispNum}��꾯�ʤ���ǽ��������١�
    my $rowcnt = @entries + 1;
    
    ####################
    # ɽ��ʸ��������
    $data .= "<h1 align=\"center\"><font color=\"$cfg{TitleColor}\">";
    if ($cfg{Logo_i} && $cfg{Logo_i}) {
        if ($ua eq 'i-mode') {
            $data .= "<img src=\"$cfg{Logo_i}\" alt=\"$blog_name mobile ver.\">";
        } else {
            $data .= "<img src=\"$cfg{Logo_o}\" alt=\"$blog_name mobile ver.\">";
        }
        $data .= "</font></h1>";
    } else {
        $data .= "$blog_name</font></h1><center>mobile ver.</center>";
    }
    
    # �����ԥ⡼��
    if ($admin_mode eq 'yes'){
        $data .= "<h2 align=\"center\"><font color=\"$cfg{TitleColor}\">�����ԥ⡼��</font></h2>";
    }
    
    if ($cfg{Dscrptn} eq "yes" && $page == 0 && $description) {
        my $tmp_data .= "<hr><center>$description</center>";
        #ñ�ʤ���Ԥ�<br>�������ִ�
        #(�֥����֥��������פ˲��Ԥ��������au��ɽ������ʤ��Զ��ؤ��н�)
        $tmp_data=~s/\r\n/<br>/g;
        $tmp_data=~s/\r/<br>/g;
        $tmp_data=~s/\n/<br>/g;
        $data .= $tmp_data;
    }
    $data .= "<hr>";
    
    # ���ƥ��ꥻ�쥯��
    if ($cfg{CatSelect} == 1) {
        $data .= "<center><form action=\"$cfg{MyName}\">";
        if ($key){
            $data .= "<input type=hidden name=\"key\" value=\"$key\">";
        }
        $data .= "<select name=\"cat\">";
        $data .= "<option value=0>���٤�";
    
        if ($mt->version_number() >= 3.11) {
            my @catlist = &get_catlist;
            for my $cat (@catlist) {
                $data .= $cat;
            }
        } else {
            my @cat_datas = ();
            require MT::Category;
            my @categories = MT::Category->load({blog_id => $cfg{Blog_ID}},
                                                    {unique => 1});
    
            for my $category (@categories) {
                # �����ԥ⡼�ɤǤʤ����ˤ���ɽ�����ƥ�����������
                if ($admin_mode ne "yes"){
                    my @nondispcats = split(",", $cfg{NonDispCat});
                    my $match_cat = 0;
                    for my $nondispcat (@nondispcats) {
                        if ($category->id == $nondispcat) {
                            $match_cat = 1;
                            last;
                        }
                    }
                    if ($match_cat > 0) {
                        next;
                    }
                }
    
                my $label;
                
                # ���ƥ���̾�����ܸ첽��$MTCategoryDescription��ɽ�����Ƥ������
                # ���ƥ��ꥻ�쥯�������Ƥ��ִ�����
                if ($cfg{CatDescReplace} eq "yes"){
                    $label = &conv_euc_z2h($category->description);
                }else{
                    $label = &conv_euc_z2h($category->label);
                }
                my $cat_id = $category->id;
                require MT::Entry;
                require MT::Placement;
                ####################
                # °���륨��ȥ꤬1�ʾ�Υ��ƥ���Τ����
                my %terms = (blog_id => $cfg{Blog_ID});
                # �����ԥ⡼�ɤǤʤ���Х��ơ�������'����'�Υ���ȥ�Τߥ������
                if ($admin_mode ne "yes"){
                    $terms{'status'} = 2;
                }
                my $count = MT::Entry->count( \%terms,
                                            { join => [ 'MT::Placement', 'entry_id',
                                            { blog_id => $cfg{Blog_ID}, category_id => $cat_id } ] });
                if ($count > 0) {
                    if ($cat != 0 && $cat_id == $cat) {
                        @cat_datas = (@cat_datas,"$cat_id,$label,$count");
                    } else {
                        @cat_datas = (@cat_datas,"$cat_id,$label,$count");
                    }
                }
            }
            
            if ($cfg{CatDescSort} eq "asc"){
                @cat_datas = sort { (split(/\,/,$a))[1] cmp (split(/\,/,$b))[1] } @cat_datas;
            }elsif ($cfg{CatDescSort} eq "desc"){
                @cat_datas = reverse sort { (split(/\,/,$a))[1] cmp (split(/\,/,$b))[1] } @cat_datas;
            }
            
            for my $cat_data (@cat_datas) {
                my @cd_tmp = split(",", $cat_data);
                
                my $tmpdata = "$cd_tmp[1]($cd_tmp[2])";
                # ����ʸ�����Ǥ֤ä��ڤ�
                if ($cfg{LenCutCat} > 0) {
                    if (MT4i::Func::lenb_euc($tmpdata) > $cfg{LenCutCat}) {
                        $tmpdata = MT4i::Func::midb_euc($cd_tmp[1], 0, $cfg{LenCutCat}-MT4i::Func::lenb_euc($cd_tmp[2])-2).'('.$cd_tmp[2].')';
                    }
                }
                if ($cat == $cd_tmp[0]){
                    $data .= "<option value=$cd_tmp[0] selected>$tmpdata";
                }else{
                    $data .= "<option value=$cd_tmp[0]>$tmpdata";
                }
            }
        }
        $data .= "</select>";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"submit\" value=\"����\"></form></center>";
        $data .= "<hr>";
    }
    
    ####################
    # ������ʸ
    
    # ������̤�0��ξ��ϥ�å�����ɽ��
    if (@entries <= 0) {
        $data .= "���Ύ��Î��ގؤ�°���뎴�ݎĎؤϤ���ޤ���";
    } else {
        my $i = 0;
        for my $entry (@entries){ # ��̤Υե��å���ɽ��
            my $title = &conv_euc_z2h($entry->title);
            $title = "untitled" if($title eq '');
            # ���񤭡����������ɤ�����Ĵ�٤�
            my $ent_status = $entry->status;
            my $d_f;
            if ($ent_status == 1) {
                $d_f = '(����)';
            } elsif ($ent_status == 3) {
                $d_f = '(������)';
            }
            $title = $d_f . $title;
            my $created_on = &conv_datetime($mt->version_number() >= 4.0 ? $entry->authored_on : $entry->created_on);
            my $comment_cnt = $entry->comment_count;
            my $ping_cnt = $entry->ping_count;
            $rowid++;
            $i++;
            my $href = &make_href("individual", $rowid, 0, $entry->id, 0);
            if ($cfg{AccessKey} eq "no" || ($cfg{AccessKey} eq "yes" && $ua ne "i-mode" && $ua ne "ezweb" && $ua ne "j-sky")) {
                $data .= "$rowid.<a href=\"$href\">$title</a>$created_on";
            } else {
                $data .= "$nostr[$i]<a href=\"$href\"$akstr[$i]>$title</a>$created_on";
            }
            if ($comment_cnt > 0 && $cfg{CommentColor} ne 'no'){ #�����ȿ���������ղ�
                $data .= "<font color=\"$cfg{CommentColor}\">[$comment_cnt]</font>";
            }
            if ($ping_cnt > 0 && $cfg{TbColor} ne 'no'){ #�ȥ�å��Хå�����������ղ�
                $data .= "<font color=\"$cfg{TbColor}\">[$ping_cnt]</font>";
            }
            $data .= "<br>";
        }
        
        # �ǽ��ڡ����λ���
        #if ($ttlcnt >= $cfg{DispNum}) {
        if ($ttlcnt > $cfg{DispNum}) {
            my $lastpage = int($ttlcnt / $cfg{DispNum});    # int()�Ǿ������ʲ����ڤ�Τ�
            my $amari = $ttlcnt % $cfg{DispNum};            # ;��λ���
            if ($amari > 0) { $lastpage++ }                # ���ޤ꤬���ä���+1
            my $ttl = $lastpage;                        # ���Υڡ�����ɽ���Ѥ��ͼ���
            $lastpage--;                                # �Ǥ�ڡ�����0����ϤޤäƤ�Τ�-1�ʤʤ󤫴�ȴ����
            
            # �ڡ�����ɽ��
            my $here = $page + 1;
            $data .= "<center>$here/$ttl</center><hr>";
        
            # �����ѥڡ������׻�
            my $nextpage = $page + 1;
            my $prevpage = $page - 1;
            
            # ���������ǽ�
            if ($rowid < $ttlcnt) {
                my $href = &make_href("", 0, $nextpage, 0, 0);
                if ($page == $lastpage - 1 && $amari > 0) {
                    $data .= "$nostr[9]<a href=\"$href\"$akstr[9]>����$amari�� &gt;</a><br>";
                } else {
                    $data .= "$nostr[9]<a href=\"$href\"$akstr[9]>����$cfg{DispNum}�� &gt;</a><br>";
                }
            }
            $rowid = $rowid - $rowcnt;
            if ($rowid > 0) {
                my $href = &make_href("", 0, $prevpage, 0, 0);
                $data .= "$nostr[7]<a href=\"$href\"$akstr[7]>&lt; ����$cfg{DispNum}��</a><br>";
            }
            if ($page > 1) {
                my $href = &make_href("", 0, 0, 0, 0);
                $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>&lt;&lt; �ǽ��$cfg{DispNum}��</a><br>";
            }
            
            # �ֺǸ�ץ�󥯤�ɽ��Ƚ��
            if ($page < $lastpage - 1) {
                my $href = &make_href("", 0, $lastpage, 0, 0);
                if ($amari > 0) {
                    $data .= "$nostr[8]<a href=\"$href\"$akstr[8]>�Ǹ��$amari�� &gt;&gt;</a><br>";
                } else {
                    $data .= "$nostr[8]<a href=\"$href\"$akstr[8]>�Ǹ��$cfg{DispNum}�� &gt;&gt;</a><br>";
                }
            }
        } else {
            $data .= "<center>1/1</center>";
        }

        # �Ƕ�Υ����Ȱ����ؤΥ��
        if ($page == 0) {
            require MT::Comment;
            my $blog_comment_cnt = MT::Comment->count({ blog_id => $cfg{Blog_ID} });
            if ($blog_comment_cnt) {
                my $href = &make_href("recentcomment", 0, 0, 0, 0);
                $data .= "<hr><a href=\"$href\">�Ƕ�Ύ��Ҏݎ�$cfg{RecentComment}��</a>";
            }
        }
    }
    
    # ��������URL�ؤΥ�󥯤�ɽ������
    if ($cfg{AdminDoor} eq "yes"){
        $data .= "<hr>";
        my $href = &make_href("admindoor", 0, 0, 0);
        $data .= "<form method=\"post\" action=\"$href\">";
        $data .= "��������URL�����<br>";
        $data .= "\AdminPassword����";
        $data .= "<br><input type=\"text\" name=\"pw_text\" istyle=3><br>";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"admindoor\">";
        $data .= "<input type=\"submit\" value=\"����\">";
        if ($key){
            $data .= "<input type=hidden name=\"key\" value=\"$key\">";
        }
        $data .= "</form>";
        
        if ($admin_mode eq "yes"){
            $data .= '<font color="red">���ʤ��ϴ�������URL������ѤߤǤ�������URL��̎ގ����ώ��������塢®�䤫�ˡ�MT4i Manager�פˤ�"AdminDoor"���ͤ�"no"���ѹ����Ƥ���������</font><br>';
        }
        if ($cfg{AdminPassword} eq "password"){
            $data .= '<font color="red">"AdminPassword"���Îގ̎��َ���"password"�����ѹ�����Ƥ��ޤ��󡣤��Τޤޤ���¾�ͤ˴�����URL���¬������ǽ�������˹⤯�ʤ�ޤ���®�䤫���ѹ����Ƥ���������</font><br>';
        }
    }
    
    #�������ѥ�˥塼
    if ($admin_mode eq "yes"){
        $data .= "<hr>";

        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"[��]Entry�ο�������\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"entryform\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
        
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        if ($email_new_comments){
            $data .= "<input type=\"submit\" value=\"[��]���ҎݎĤΎҎ������Τ���ߤ���\">";
        }else{
            $data .= "<input type=\"submit\" value=\"[��]���ҎݎĤΎҎ������Τ�Ƴ�����\">";
        }
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"email_comments\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";

        $data .= "<hr>";
    }
    
    &htmlout;
}

########################################
# Sub Individual - ñ�����ڡ���������
########################################

sub individual {
    # �������ä���Υ����������ĥ�����������ͭ���ξ���$cfg{DispNum}��6�ʲ��ˤ���
    if ($cfg{AccessKey} eq "yes" && ($ua eq "i-mode" || $ua eq "j-sky" || $ua eq "ezweb")) {
        if ($cfg{DispNum} > 6) {
            $cfg{DispNum} = 6;
        }
    }
    my $rowid;
    if ($no) {
        $rowid = $no;
        $no--;
    } else {
        $no = 0;
        my $ttlcnt = &get_ttlcnt;
        FOUND: while ($ttlcnt > 0) {
            my @entries = &get_entries($no, $cfg{DispNum});
            if (@entries <= 0) {
                last;
            }
            for my $entry (@entries) {
                $no++;
                if ($entry->id == $eid) {
                    last FOUND;
                }
            }
            $ttlcnt -= $cfg{DispNum};
        }
        $rowid = $no;
        $no--;
    }
    
    ####################
    # �����μ���
    require MT::Entry;
    my $entry = MT::Entry->load($eid);

    # ������̤�0��ξ��ϥ�å�����ɽ������STOP��ͭ�����ʤ����ɤʡ�
    if (!$entry) {
        if ($hentities == 1) {
            $data = 'Entry ID \''.encode_entities($eid).'\' �������Ǥ���';
        } else {
            $data = 'Entry ID \''.$eid.'\' �������Ǥ���';
        }
        &errorout;
        exit;      # exit����
    }

    # ��̤��ѿ��˳�Ǽ
    my $title = &conv_euc_z2h($entry->title);
    my $text = &conv_euc_z2h(MT->apply_text_filters($entry->text, $entry->text_filters));
    my $text_more = &conv_euc_z2h(MT->apply_text_filters($entry->text_more, $entry->text_filters));
    my $convert_breaks = $entry->convert_breaks;
    my $created_on = &conv_datetime($mt->version_number() >= 4.0 ? $entry->authored_on : $entry->created_on);
    my $comment_cnt = $entry->comment_count;
    my $ping_cnt = $entry->ping_count;
    # ��������Ƶ�ǽ������OFF����Ƥ������allow_comments��Closed��
    my $ent_allow_comments;
    if ($cfg{ArrowComments} == 1) {
        $ent_allow_comments = $entry->allow_comments;
    } else {
        $ent_allow_comments = 2;
    }
    my $ent_status = $entry->status;
    
    # ��ʸ���ɵ����ĤˤޤȤ��
    if($text_more){
        $text = "<p>$text</p><p>$text_more</p>";
    }
    
    ####################
    # ��󥯤�URL��chtmltrans��ͳ���Ѵ�
    $text = &conv_redirect($text, $rowid, $eid);
    
    ####################
    # <img>����������URL�Υ���å����%2F���Ѵ�
    if ($imk != 2) {
        $text = &img_url_conv($text);
    }
    
    ####################
    # �����ν���������
    
    my $href;
    
    # a������ޤ᤿���ALT��ɽ���������ؤΥ��
    if ($imk == 2) {
        $text =~ s/<a[^>]*><img[^>]*src=\n*["']http:\/\/([^"'>]*)["'][^>]*alt=\n*["']([^"'>]*)["'][^>]*><\/a>/&lt;<a href="http:\/\/pic.to\/$1">������$2<\/a>&gt;/ig;
        $text =~ s/<a[^>]*><img[^>]*alt=\n*["']([^"'>]*)["'][^>]*src=\n*["']http:\/\/([^"'>]*)["'][^>]*><\/a>/&lt;<a href="http:\/\/pic.to\/$2">������$1<\/a>&gt;/ig;
        
        # img�����Τߤν��ALT��ɽ���������ؤΥ��
        $text =~ s/<img[^>]*src=\n*["']http:\/\/([^"'>]*)["'][^>]*alt=\n*["']([^"'>]*)["'][^>]*>/&lt;<a href="http:\/\/pic.to\/$1">������$2<\/a>&gt;/ig;
        $text =~ s/<img[^>]*alt=\n*["']([^"'>]*)["'][^>]*src=\n*["']http:\/\/([^"'>]*)["'][^>]*>/&lt;<a href="http:\/\/pic.to\/$2">������$1<\/a>&gt;/ig;
        
        # a������ޤ᤿��������ؤΥ��
        $text =~ s/<a[^>]*><img[^>]*src=\n*["']http:\/\/([^"'>]*)["'][^>]*><\/a>/&lt;<a href="http:\/\/pic.to\/$1">����<\/a>&gt;/ig;
        
        # img�����Τߤν�������ؤΥ��
        $text =~ s/<img[^>]*src=\n*["']http:\/\/([^"'>]*)["'][^>]*>/&lt;<a href="http:\/\/pic.to\/$1">����<\/a>&gt;/ig;
    } else {
        $href = &make_href("image", $rowid, 0, $eid, 0);
        $text =~ s/<a[^>]*><img[^>]*src=\n*["']([^"'>]*)["'][^>]*alt=\n*["']([^"'>]*)["'][^>]*><\/a>/&lt;<a href="$href&amp;img=$1">������$2<\/a>&gt;/ig;
        $text =~ s/<a[^>]*><img[^>]*alt=\n*["']([^"'>]*)["'][^>]*src=\n*["']([^"'>]*)["'][^>]*><\/a>/&lt;<a href="$href&amp;img=$2">������$1<\/a>&gt;/ig;
        
        # img�����Τߤν��ALT��ɽ���������ؤΥ��
        $text =~ s/<img[^>]*src=\n*["']([^"'>]*)["'][^>]*alt=\n*["']([^"'>]*)["'][^>]*>/&lt;<a href="$href&amp;img=$1">������$2<\/a>&gt;/ig;
        $text =~ s/<img[^>]*alt=\n*["']([^"'>]*)["'][^>]*src=\n*["']([^"'>]*)["'][^>]*>/&lt;<a href="$href&amp;img=$2">������$1<\/a>&gt;/ig;
        
        # a������ޤ᤿��������ؤΥ��
        $text =~ s/<a[^>]*><img[^>]*src=\n*["']([^"'>]*)["'][^>]*><\/a>/&lt;<a href="$href&amp;img=$1">����<\/a>&gt;/ig;
        
        # img�����Τߤν�������ؤΥ��
        $text =~ s/<img[^>]*src=\n*["']([^"'>]*)["'][^>]*>/&lt;<a href="$href&amp;img=$1">����<\/a>&gt;/ig;
    }
    
    ####################
    # �����Ѵ���
    if($convert_breaks eq '__default__' || ($convert_breaks ne '__default__' && $convert_breaks ne '0' && $convert_paras eq '__default__')) {
        # bq�������ο��ѹ�
        if ($cfg{BqColor}) {
            $text=~s/<blockquote>/<blockquote><font color="$cfg{BqColor}">/ig;
            $text=~s/<\/blockquote>/<\/font><\/blockquote>/ig;
        }
        # bq������p�����ؤ��Ѵ�
        if ($cfg{BQ2P} eq "yes") {
            $text=~s/<blockquote>/<p>/ig;
            $text=~s/<\/blockquote>/<\/p>/ig;
        } else {
            # bq���������;�פ�br��������
            $text=~s/<br><br><blockquote>/<blockquote>/ig;
            $text=~s/<br><blockquote>/<blockquote>/ig;
            $text=~s/<\/blockquote><br><br>/<\/blockquote>/ig;
            $text=~s/<p><blockquote>/<blockquote>/ig;
            $text=~s/<\/blockquote><\/p>/<\/blockquote>/ig;
        }
        # p���������;�פ�br��������
        $text=~s/<br \/><br \/><p>/<p>/ig;
        $text=~s/<br \/><p>/<p>/ig;
        $text=~s/<\/p><br \/><br \/>/<\/p>/ig;
        $text=~s/<br \/><\/p>/<\/p>/ig;
        # ul���������;�פ�br��������
        $text=~s/<br \/><br \/><ul>/<ul>/ig;
        $text=~s/<br \/><ul>/<ul>/ig;
        $text=~s/<ul><br \/>/<ul>/ig;
        $text=~s/<\/ul><br \/><br \/>/<\/ul>/ig;
        # ol���������;�פ�br��������
        $text=~s/<br \/><br \/><ol>/<ol>/ig;
        $text=~s/<br \/><ol>/<ol>/ig;
        $text=~s/<ol><br \/>/<ol>/ig;
        $text=~s/<\/ol><br \/><br \/>/<\/ol>/ig;
        # li�Ĥ���������
        $text=~s/<\/li>//ig;
    }
    
    ####################
    # ��ʸʬ�����
    if (MT4i::Func::lenb_euc($text) > $cfg{SprtLimit}) {
        $text = &separate($text, $rowid);
    }
    
    ####################
    # ɽ��ʸ��������
    $data .= "<h4>";
    
    # ������������α����ʤ鵭���ֹ�򿶤�
    if ($mode eq 'individual') {
        $data .= "$rowid.";
    }
    
    # ���񤭡����������ɤ�����Ĵ�٤�
    my $d_f;
    if ($ent_status == 1) {
        $d_f = '(����)';
    } elsif ($ent_status == 3) {
        $d_f = '(������)';
    }
    
    $data .= "$d_f$title";
    
    # ���ƥ���̾��ɽ��
    if ($cfg{IndividualCatLabelDisp} eq 'yes') {
        my $cat_label = &check_category($entry);
        $data .= "[$cat_label]";
    }
    
    if ($cfg{IndividualAuthorDisp} eq 'yes') {
        # Author��nickname������С������ɽ����̵�����name��ɽ������
        require MT::Author;
        my $author = MT::Author->load({ id => $entry->author_id });
        my $author_name;
        
        if ($author){
            if ($author->nickname){
                $author_name = conv_euc_z2h($author->nickname);
            }else{
                $author_name = $author->name;
            }
            $data .= " by ".$author_name;
        }
    }
    
    $data .= "$created_on</h4>";
    $data .= "<hr>";
    $data .= "$text";
    
    my $ttlcnt;
    # ������������α����ʤ鵭���ֹ�򿶤�
    if ($mode eq 'individual') {
        # ��������
        $ttlcnt = &get_ttlcnt;
        
        # ����ȥ꡼��ɽ��
        $data .= "<center>$rowid/$ttlcnt</center><hr>";
    } else {
        $data .= "<hr>";
    }
    
    #####################
    # None�Ǥ���Ƥ�ɽ����̵����Open�ʤ�ξ��OK��Closed��ɽ���Τ�
    # $comment_cnt���� None=0,Open=1,Closed=2
    # MT3.2�ʹߤǤ� Closed=2 ���ѻߤ��줿���ͤʤΤ��б� 2006/06/21
    if ($ent_allow_comments > 0 || ($ent_allow_comments == 0 && $mt->version_number() >= 3.2) ){
        if ($comment_cnt > 0) {
            if ($mode eq 'individual') {
                $href = &make_href("comment", $rowid, 0, $eid, 0);
            } elsif ($mode eq 'individual_rcm') {
                $href = &make_href("comment_rcm", $rowid, 0, $eid, 0);
            } elsif ($mode eq 'individual_lnk') {
                $href = &make_href("comment_lnk", $rowid, 0, $eid, $ref_eid);
            }
            if ($mode ne 'ainori') {
                # �����Τ���ϥ����Ȼ��ȤǤ��ʤ��褦�ˡ�
                # ���Τäƿ������ݤ����餵�á�
                $data .= "$nostr[8]<a href=\"$href\"$akstr[8]>���Ҏݎ�($comment_cnt)</a><hr>";
            }
        } elsif ($ent_allow_comments == 1) {
            if ($mode eq 'individual') {
                $href = &make_href("postform", $rowid, 0, $eid, 0);
            } elsif ($mode eq 'individual_rcm') {
                $href = &make_href("postform_rcm", $rowid, 0, $eid, 0);
            }
            $data .= "$nostr[8]<a href=\"$href\"$akstr[8]>���Ҏݎ����</a><hr>";
            # ���⡼�ɡ�comment_lnk�פλ��ϥ�������ƤǤ��ʤ���
            # ��������Ū�ʤ�����饳���Ƚ񤯤���̵���Ǥ��硢���֤�
        }
    }
    
    # Trackback
    if ($ping_cnt > 0) {
        $href = &make_href("trackback", $rowid, 0, $eid);
        $data .= "$nostr[5]<a href=\"$href\"$akstr[5]>�Ď׎����ʎގ���($ping_cnt)</a><hr>";
    }

    # �����ԤΤߡ�Entry�Խ����õ�פ���ǽ
    if ($admin_mode eq "yes"){
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"[��]����Entry���Խ�\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"entryform\">";
        $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
        $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"[��]����Entry����\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"confirm_entry_del\">";
        $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
        $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
    }
    
    if ($mode eq 'individual') {
        # ������������α���
        # �����ѥ���ȥ꡼NO����
        my $nextno = $rowid + 1;
        my $prevno = $rowid - 1;
        
        # �����ѥ���ȥ꡼ID���С�prev��next�����÷����֤äƤ���Τ���ա�
        my $nextid;
        my $previd;
        my $next = $entry->previous(1);
        my $prev = $entry->next(1);
        if ($cat) {
            my $category = MT::Category->load($cat);
            while ($next && !$next->is_in_category($category)){
                $next = $next->previous(1);
            }
            while ($prev && !$prev->is_in_category($category)){
                $prev = $prev->next(1);
            }
        } elsif ($cfg{NonDispCat}) {
            # ��ɽ�����ƥ��꤬���ꤵ��Ƥ�����
            # ��ɽ�����ƥ���Υꥹ�Ȥ򥵥֥��ƥ����ޤ�Ƽ�������
            my @nondispcats = &get_nondispcats();
            
            # ���뤰��󤷤���ɽ�����ƥ�����͹礻
            while ($next) {
                # ����ȥ�Υ��ƥ������
                my @places = MT::Placement->load({ entry_id => $next->id });
                if (@places) {
                    my $match = 0;
                    foreach my $place (@places) {
                        foreach my $nondispcat (@nondispcats) {
                            if ($place->category_id == $nondispcat) {
                                $match++;
                                last;
                            }
                        }
                    }
                    if ($match < @places) {
                        last;
                    } else {
                        $next = $next->previous(1);
                    }
                } else {
                    last;
                }
            }
            while ($prev) {
                # ����ȥ�Υ��ƥ������
                my @places = MT::Placement->load({ entry_id => $prev->id });
                if (@places) {
                    my $match = 0;
                    foreach my $place (@places) {
                        foreach my $nondispcat (@nondispcats) {
                            if ($place->category_id == $nondispcat) {
                                $match++;
                                last;
                            }
                        }
                    }
                    if ($match < @places) {
                        last;
                    } else {
                        $prev = $prev->next(1);
                    }
                } else {
                    last;
                }
            }
        }
        if ($next) {
            $nextid = $next->id;
        }
        if ($prev) {
            $previd = $prev->id;
        }
        
        if($rowid < $ttlcnt) {
            $href = &make_href("individual", $nextno, 0, $nextid, 0);
            $data .= "$nostr[9]<a href=\"$href\"$akstr[9]>���ε����� &gt;</a><br>";
        }
        if($rowid > 1) {
            $href = &make_href("individual", $prevno, 0, $previd, 0);
            $data .= "$nostr[7]<a href=\"$href\"$akstr[7]>&lt; ���ε�����</a><br>";
        }
        # �ڡ���������
        $page = int($no / $cfg{DispNum});    # int()�Ǿ������ʲ����ڤ�Τ�
        
        $href = &make_href("", 0, $page, 0, 0);
        $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>���������</a>";
    } elsif ($mode eq 'individual_rcm') {
        # �Ƕᥳ���Ȱ�������α���
        $href = &make_href("recentcomment", 0, 0, 0, 0);
        $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>�ǶᎺ�Ҏݎİ��������</a>";
    } elsif ($mode eq 'individual_lnk') {
        # �������󥯤���α���
        $href = &make_href("individual", $rowid, 0, $ref_eid, 0);
        $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>�؎ݎ����ε��������</a>";
    } elsif ($mode eq 'ainori') {
        # �����Τ���ϥ�ե�������
        $href = $ENV{'HTTP_REFERER'};
        $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>�؎ݎ��������</a>";
    }
    
    &htmlout;
}

########################################
# Sub Comment - ����������
########################################

sub comment {
    my $rowid = $no;
    
    ####################
    # entry id�μ���
    require MT::Entry;
    my $entry = MT::Entry->load($eid);

    # ������̤�0��ξ��ϥ�å�����ɽ������STOP��ͭ�����ʤ����ɤʡ�
    if ($entry <= 0) {
        if ($hentities == 1) {
            $data = 'Entry ID \''.encode_entities($eid).'\' �������Ǥ���';
        } else {
            $data = 'Entry ID \''.$eid.'\' �������Ǥ���';
        }
        &errorout;
        exit;      # exit����
    }

    # ��̤��ѿ��˳�Ǽ
    my $ent_title = &conv_euc_z2h($entry->title);
    my $ent_created_on = &conv_datetime($mt->version_number() >= 4.0 ? $entry->authored_on : $entry->created_on);
    my $ent_id = $entry->id;
    # ��������Ƶ�ǽ������OFF����Ƥ������allow_comments��Closed��
    my $ent_allow_comments;
    if ($cfg{ArrowComments} == 1) {
        $ent_allow_comments = $entry->allow_comments;
    } else {
        $ent_allow_comments = 2;
    }
    my $ent_status = $entry->status;
    
    ####################
    # �����Ȥμ���
    my @comments;
    # �����ԥ⡼�ɤǤϥ����Ȥ�ս�ɽ������
    if ($admin_mode eq "yes"){
        @comments = get_comments($ent_id, '', 'descend', 1);
    }else{
        @comments = get_comments($ent_id, '', $sort_order_comments, 1);
    }
    
    my $author;
    my $txt;
    my $created_on;
    my $text;
    for my $comment (@comments) {
        $author = &conv_euc_z2h($comment->author);
        $txt = &conv_euc_z2h($comment->text);
        $created_on = &conv_datetime($comment->created_on);
        $text .= "<hr>by $author$created_on<br><br>$txt";
        
        # �����ԤΤߡ֥����Ⱦõ��������ǽ
        if ($admin_mode eq "yes"){
            $text .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
            $text .= "<input type=\"submit\" value=\"[��]���Ύ��ҎݎĤ���\">";
            $text .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
            $text .= "<input type=\"hidden\" name=\"mode\" value=\"confirm_comment_del\">";
            $text .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
            $text .= "<input type=\"hidden\" name=\"page\" value=\"".$comment->id."\">";
            $text .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
            $text .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
            $text .= "</form>";
        }
    }

    ####################
    # �����Ѵ���
    if($convert_paras_comments eq '__default__'){
        # ���Ԥ�br�����ؤ��Ѵ�
        $text=~s/\r\n/<br>/g;
        $text=~s/\r/<br>/g;
        $text=~s/\n/<br>/g;
    }

    ####################
    # ��󥯤�URL��chtmltrans��ͳ���Ѵ�
    $text = &conv_redirect($text, $rowid, $eid);
    
    ####################
    # <_ahref>��<a href>���᤹
    $text=~s/_ahref/a href/g;
    
    ####################
    # ��ʸʬ�����
    if (MT4i::Func::lenb_euc($text) > $cfg{SprtLimit}) {
        $text = &separate($text, $rowid);
    }
    
    ####################
    # ɽ��ʸ��������
    $data .= "<h4>";
    if ($rowid) {
        $data .= "$rowid.";
    }
    if ($admin_mode eq "yes"){
        $data .= "$ent_title$ent_created_on�ؤΎ��Ҏݎ�(��������)</h4>";
    }else{
        $data .= "$ent_title$ent_created_on�ؤΎ��Ҏݎ�</h4>";
    }
    $data .= "$text<hr>";
    if ($ent_allow_comments == 1){
        if ($mode eq 'comment') {
            my $href = &make_href("postform", $rowid, 0, $eid, 0);
            $data .= "$nostr[8]<a href=\"$href\"$akstr[8]>���Ҏݎ����</a><hr>";
        } elsif ($mode eq 'comment_rcm') {
            my $href = &make_href("postform_rcm", $rowid, 0, $eid, 0);
            $data .= "$nostr[8]<a href=\"$href\"$akstr[8]>���Ҏݎ����</a><hr>";
        }
            # ���⡼�ɡ�comment_lnk�פλ��ϥ�������ƤǤ��ʤ���
            # ��������Ū�ʤ�����饳���Ƚ񤯤���̵���Ǥ��硢���֤�
    }
    my $href = &make_href("individual", $rowid, 0, $eid, 0);
    if ($mode eq 'comment') {
        $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>���������</a>";
    } else {
        if ($mode eq 'comment_rcm') {
            $href =~ s/individual/individual_rcm/ig;
        } elsif ($mode eq 'comment_lnk') {
            $href = &make_href("individual_lnk", $rowid, 0, $eid, $ref_eid);
        }
        $data .= "$nostr[7]<a href=\"$href\"$akstr[7]>���������ɤ�</a><hr>";
        if ($mode eq 'comment_rcm') {
            my $href = &make_href("recentcomment", 0, 0, 0, 0);
            $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>�ǶᎺ�Ҏݎİ��������</a>";
        } elsif ($mode eq 'comment_lnk') {
            my $href = &make_href("individual", $rowid, 0, $ref_eid, 0);
            $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>�؎ݎ����ε��������</a>";
        }
    }

    &htmlout;
}

########################################
# Sub Recent_Comment - �����ȤޤȤ��ɤ�
########################################

sub recent_comment {
    
    ####################
    # �����Ȥμ���
    my @comments = get_comments('', $cfg{RecentComment}, 'descend', 1);
    
    my $text;
    require MT::Entry;
    for my $comment (@comments) {
        my $author = &conv_euc_z2h($comment->author);
        my $created_on = &conv_datetime($comment->created_on);
        my $eid = $comment->entry_id;
        
        my $entry = MT::Entry->load($eid);
        my $entry_title = &conv_euc_z2h($entry->title);
        
        my $href = &make_href("comment_rcm", 0, 0, $eid, 0);
        $text .= "<hr>Re:<a href=\"$href\">$entry_title</a><br>by $author$created_on";
    }

    ####################
    # ɽ��ʸ��������
    $data .= "<h4>�Ƕ�Ύ��Ҏݎ�$cfg{RecentComment}��</h4>";
    $data .= "$text<hr>";
    
    my $href = &make_href("", 0, 0, 0, 0);
    $data .= "<br>$nostr[0]<a href='$href'$akstr[0]>���������</a>";

    &htmlout;
}

########################################
# Sub Trackback - �ȥ�å��Хå�ɽ��
########################################

sub trackback {
    
    my $rowid = $no;
    
    ####################
    # �ȥ�å��Хå��μ���
    require MT::Trackback;
    my $tb = MT::Trackback->load(
            { blog_id => $cfg{Blog_ID} , entry_id => $eid},
            { 'sort' => 'created_on',
              direction => 'descend',
              unique => 1,
              limit => 1 });
    
    my @tbpings;
    require MT::TBPing;
    if ($mt->version_number() >= 3.2) {
        @tbpings = MT::TBPing->load(
                { blog_id => $cfg{Blog_ID},
                  tb_id => $tb->id,
                  visible => 1,
                  junk_status => [ 0, 1 ] },
                { 'sort' => 'created_on',
                  direction => 'descend',
                  unique => 1,
                  limit => $cfg{RecentTB},
                  'range_incl' => { 'junk_status' => 1 } });
    } else {
        @tbpings = MT::TBPing->load(
                { blog_id => $cfg{Blog_ID},
                  tb_id => $tb->id },
                { 'sort' => 'created_on',
                  direction => 'descend',
                  unique => 1,
                  limit => $cfg{RecentTB} });
    }
    
    my $text;
    for my $tbping (@tbpings) {
        my $ping_title = &conv_euc_z2h($tbping->title);
        my $ping_excerpt = &conv_euc_z2h($tbping->excerpt);
        my $ping_name = &conv_euc_z2h($tbping->blog_name);
        my $ping_tracked = conv_datetime($tbping->created_on);
        my $ping_sourceurl = $tbping->source_url;
        my $ping_id = $tbping->id;
        
        $text .= "<hr>$ping_title<br>$ping_excerpt<br><a href=\"$ping_sourceurl\">Weblog:$ping_name</a><br>Tracked:$ping_tracked<br>";
        # �����ԤΤߡ֥ȥ�å��Хå������������ǽ
        if ($admin_mode eq "yes"){
            $text .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
            $text .= "<input type=\"submit\" value=\"[��]����TB����\">";
            $text .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
            $text .= "<input type=\"hidden\" name=\"mode\" value=\"confirm_trackback_del\">";
            $text .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
            $text .= "<input type=\"hidden\" name=\"page\" value=\"$ping_id\">";
            $text .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
            $text .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
            $text .= "</form>";
        }
    }
    
    ####################
    # ��󥯤�URL��chtmltrans��ͳ���Ѵ�
    $text = &conv_redirect($text, $rowid, $eid);
    
    ####################
    # <_ahref>��<a href>���᤹
    $text=~s/_ahref/a href/g;
    
    ####################
    # ɽ��ʸ��������
    if (@tbpings < $cfg{RecentTB}){
        $cfg{RecentTB} = @tbpings;
    }
    
    $data .= "<h4>����Entry�ؤκǶ�ΎĎ׎����ʎގ���$cfg{RecentTB}��(��������)</h4>";
    $data .= "$text<hr>";
    
    my $href = &make_href("individual", $rowid, 0, $eid);
    $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>���������</a>";
    
    &htmlout;
}

#############################################
# Sub Get_Entries - ����ȥ�μ���
# ������ : ���ե��å�
# ������� : �����Ŀ�
# �����Ԥξ��ˤϡ�status�θ�����
#############################################
sub get_entries {
    my @ent;
    require MT::Entry;
    
    my %terms = (blog_id => $cfg{Blog_ID});
    my %arg = (
            direction => 'descend',
            limit => $_[1],
            offset => $_[0],
    );
    $arg{'sort'} = $mt->version_number() >= 4.0 ? 'authored_on' : 'created_on';
    
    if ($cat != 0) {
        # ���ƥ�����ꤢ��
        $arg{'join'} = [ 'MT::Placement', 'entry_id',
                 { blog_id => $cfg{Blog_ID}, category_id => $cat }, { unique => 1 } ];
    }
    
    if ($admin_mode eq "yes"){
        @ent = MT::Entry->load(\%terms, \%arg);
    } else {
        $terms{'status'} = 2;
        if ($cat == 0) {
            # ���ƥ������ʤ�
            if ($cfg{NonDispCat}) {
                # ��ɽ�����ƥ�����ꤢ��
                my %arg = (
                    direction => 'descend',
                );
                $arg{'sort'} = $mt->version_number() >= 4.0 ? 'authored_on' : 'created_on';
                my @entries = MT::Entry->load(\%terms, \%arg);
                
                # ��ɽ�����ƥ���Υꥹ�Ȥ򥵥֥��ƥ����ޤ�Ƽ�������
                my @nondispcats = &get_nondispcats();
                
                my $count = 1;
                foreach my $entry (@entries) {
                    # ����ȥ�Υ��ƥ������
                    my @places = MT::Placement->load({ entry_id => $entry->id });
                    if (@places) {
                        my $match_cat = 0;
                        foreach my $place (@places) {
                            foreach my $nondispcat (@nondispcats) {
                                if ($place->category_id == $nondispcat) {
                                    $match_cat++;
                                    last;
                                }
                            }
                        }
                        if ($match_cat < @places) {
                            if ($count > $_[0]) {
                                push @ent, $entry;
                            }
                            $count++;
                        }
                    } else {
                        # Non-Category��ɽ��
                        if ($count > $_[0]) {
                            push @ent, $entry;
                        }
                        $count++;
                    }
                    if ($count == $_[1] + $_[0] + 1) {
                        last;
                    }
                }
            } else {
                # ��ɽ�����ƥ������ʤ�
                @ent = MT::Entry->load(\%terms, \%arg);
            }
        } else {
            # ���ƥ�����ꤢ��
            @ent = MT::Entry->load(\%terms, \%arg);
        }
    }
    
    return @ent;
}

#############################################
# Sub Get_Comments - �����Ȥμ���
# ������ : ����ȥ꡼ID
# ������� : �����Ŀ�
# �軰���� : �����ȹ߽硿����
# ��Ͱ��� : visible�ͥ����å���̵ͭ 1:ͭ 0:̵
#############################################
sub get_comments {
    my %arg1;
    my %arg2;
    
    $arg1{'blog_id'} = $cfg{Blog_ID};
    if ($_[0] ne '') {
        $arg1{'entry_id'} = $_[0];
    }
    if ($mt->version_number() >= 3.0 && $_[3] == 1) {
        $arg1{'visible'} = 1;
    }
    
    $arg2{'sort'} = 'created_on';
    $arg2{'direction'} = $_[2];
    $arg2{'unique'} = 1;
    if ($_[1] ne '' && $cfg{NonDispCat} eq '') {
        $arg2{'limit'} = $_[1];
    }
    
    require MT::Comment;
    my @cmnt = MT::Comment->load(\%arg1, \%arg2);
    
    # ��ɽ�����ƥ��꤬���ꤵ��Ƥ��뤫
    my @comments;
    if (!$cfg{NonDispCat}) {
        @comments = @cmnt;
    } else {
        my @nondispcats = split(",", $cfg{NonDispCat});
        my $count = 0;
        foreach my $comment (@cmnt) {
            my @places = MT::Placement->load({ entry_id => $comment->entry_id });
            if (@places) {
                my $match_cat = 0;
                foreach my $place (@places) {
                    foreach my $nondispcat (@nondispcats) {
                        if ($place->category_id == $nondispcat) {
                            $match_cat++;
                            last;
                        }
                    }
                }
                if (@places > $match_cat) {
                    push @comments, $comment;
                    $count++;
                }
            } else {
                # Non-Category��ɽ��
                push @comments, $comment;
                $count++;
            }
            if ($count == $_[1]) {
                last;
            }
        }
    }
    
    return @comments;
}

##############################################
# Sub Get_Ttlcnt - ��������μ���
##############################################
sub get_ttlcnt {
    require MT::Entry;
    require MT::Placement;
    my %terms;
    $terms{blog_id} = $cfg{Blog_ID};
    if ($admin_mode eq 'no') {
        $terms{status} = 2;
    }
    my %arg = (
            direction => 'descend',
            unique => 1,
    );
    $arg{'sort'} = $mt->version_number >= 4.0 ? 'authored_on' : 'created_on';
    if ($cat == 0) {
        #���ƥ���ʤ�
        if ($cfg{NonDispCat}) {
            # ��ɽ�����ƥ�����ꤢ��
            my @entries = MT::Entry->load(\%terms, \%arg);

            # ��ɽ�����ƥ���Υꥹ�Ȥ򥵥֥��ƥ����ޤ�Ƽ�������
            my @nondispcats = &get_nondispcats();
            
            my @ent;
            foreach my $entry (@entries) {
                # ����ȥ�Υ��ƥ������
                my @places = MT::Placement->load({ entry_id => $entry->id });
                if (@places) {
                    my $match_cat = 0;
                    foreach my $place (@places) {
                        foreach my $nondispcat (@nondispcats) {
                            if ($place->category_id == $nondispcat) {
                                $match_cat++;
                                last;
                            }
                        }
                    }
                    if ($match_cat < @places) {
                        push @ent, $entry;
                    }
                } else {
                    # Non-Category��ɽ��
                    push @ent, $entry;
                }
            }
            return @ent;
        } else {
            # ��ɽ�����ƥ���λ���ʤ�
            return MT::Entry->count(\%terms, \%arg);
        }
    } else {
        #���ƥ��ꤢ��
        $arg{'join'} = [ 'MT::Placement', 'entry_id',
                 { blog_id => $cfg{Blog_ID}, category_id => $cat }, { unique => 1 } ];
        return MT::Entry->count(\%terms, \%arg);
    }
}

##############################################
# Sub Make_Href - HREFʸ����κ���
# ������ : mode
# ������� : no
# �軰���� : page
# ��Ͱ��� : eid
# ��ް��� : ref_eid
#
# �㳰�Ȥ��ơ�$mode��"post"�ξ��ˤ�
# id����Ϥ��ޤ���
##############################################
sub make_href
{
    my $h = "$cfg{MyName}";
    if ($_[0] ne "post" && $_[0] ne "post_rcm" && $_[0] ne "post_lnk"){
        $h .= "?id=$cfg{Blog_ID}";
        if ($cat != 0) {
            $h .= "&amp;cat=$cat";
        }
        if ($_[0] ne "" && $_[0] ne "main") {
            $h .= "&amp;mode=$_[0]";
        }
        if ($_[1] != 0) {
            $h .= "&amp;no=$_[1]";
        }
        if ($_[2] != 0) {
            $h .= "&amp;page=$_[2]";
        }
        if ($_[3] != 0) {
            $h .= "&amp;eid=$_[3]";
        }
        if ($_[4] != 0) {
            $h .= "&amp;ref_eid=$_[4]";
        }
        if ($key){
            $h .= "&amp;key=$key";
        }
    }
    return $h;
}

########################################
# Sub Image - ����ɽ��
########################################

sub image {
    # PerlMagick ��̵����в����̾�ɽ�������Ϥ��ʤ�
    if ($imk == 0){
        $img =~ s/\%2F/\//ig;
        if ($hentities == 1) {
            $data .='<p><img src="'.encode_entities($img).'"></p>';
        } else {
            $data .='<p><img src="'.$img.'"></p>';
        }
    }else{
        # /��%2F�˺ƥ��󥳡���
        $img =~ s/\//\%2F/ig;
        if ($hentities == 1) {
            $data .="<p><img src=\"./$cfg{MyName}?mode=img_cut&amp;id=$cfg{Blog_ID}&amp;img=".encode_entities($img)."\"></p>";
        } else {
            $data .="<p><img src=\"./$cfg{MyName}?mode=img_cut&amp;id=$cfg{Blog_ID}&amp;img=".$img."\"></p>";
        }
    }
    my $href = &make_href("individual", $no, 0, $eid, 0);
    $data .="$nostr[0]<a href=\"$href\"$akstr[0]>���</a>";
    
    &htmlout;
}

########################################
# Sub Image_Cut - �����̾�ɽ��
########################################

sub image_cut {
    $img =~ s/\%2F/\//ig;
    my $url = $img;
    $url =~ s/http:\/\///;
    my $host = substr($url, 0, index($url, "/"));
    my $path = substr($url, index($url, "/"));
    $data = "";

    ####################
    # �ۥ���̾�ִ�
    if ($host eq $cfg{Photo_Host_Original}){
        $host = $cfg{Photo_Host_Replace};
    }
    
    ####################
    # �����ɤ߹��ߤ�LWP�⥸�塼����Ѥ��ѹ�
    require HTTP::Request;
    require LWP::UserAgent;
    my $ua = LWP::UserAgent->new;
    $url = 'http://'.$host.$path;
    my $request = HTTP::Request->new(GET => $url);
    my $response = $ua->request($request);
    
    if ($response->is_success) {
        $data = $response->as_string;
        $data =~ /(.*?\r?\n)\r?\n(.*)/s;
        $data = $2;
    } else {
        print "Content-type: text/html;\n\nHTTP Error:LWP";
        return;
    }
    
    my @blob = $data;
    
    ####################
    # vodafone�����굡��˸¤�png������ʳ���jpg���Ѵ�
    # �������˴ؤ�餺��png�⤷����jpg���Ѵ�����褦���ѹ�
    my $image = Image::Magick->new;
    $image->BlobToImage(@blob);
    
    # �ǥ�����ʤɤΥ��ץꥱ����������κ��
    if (Image::Magick->VERSION >= 6.0) {
        $image->Strip();
    } else {
        $image->Profile( name=>'*' );
        $image->Comment('');
    }
    
    my $format;
    
    if ($png_flag){
        $image->Set(magick=>'png');
        $format = 'png';
        $cfg{PhotoWidth} = $cfg{PngWidth};
    }else{
        $image->Set(magick=>'jpg');
        $format = 'jpeg';
    }
    
    # ���͡�http://deneb.jp/Perl/mobile/
    my $start_pos = 0;
    my $user_agent = $ENV{'HTTP_USER_AGENT'};
    my $cache_limit = -1024 + MT4i::Func::calc_cache_size( $user_agent );
    # ���������˥���å�������ϰ���ʤ�̾��������ʤ�
    @blob = $image->ImageToBlob();
    if ( $cache_limit <  length($blob[0]) ) {
        foreach my $i ( $start_pos ..19 ) {
            my $img2 = $image->Clone();
            my $ratio = 1-$i*0.05;
            my $x = $cfg{PhotoWidth} * $ratio;
            $img2->Scale($x);
            @blob = $img2->ImageToBlob();
            if ( $cache_limit >=  length($blob[0]) ) {
                last;
            }
        }
    }

    print "Content-type: image/$format\n";
    print "Content-length: ",length($blob[0]),"\n\n";
    binmode STDOUT;
    print STDOUT $blob[0];
}

########################################
# Sub Postform - ��������ƥե�����
########################################

sub postform {
    my $rowid = $no;
    
    # Entry����
    require MT::Entry;
    my $entry = MT::Entry->load($eid);

    # ������̤�0��ξ��ϥ�å�����ɽ������STOP��ͭ�����ʤ����ɤʡ�
    if ($entry <= 0) {
        if ($hentities == 1) {
            $data = 'Entry ID \''.encode_entities($eid).'\' �������Ǥ���';
        } else {
            $data = 'Entry ID \''.$eid.'\' �������Ǥ���';
        }
        &errorout;
        exit;      # exit����
    }

    # ��̤��ѿ��˳�Ǽ
    my $ent_title = &conv_euc_z2h($entry->title);
    my $ent_created_on = &conv_datetime($mt->version_number >= 4.0 ? $entry->authored_on : $entry->created_on);

    ####################
    # ɽ��ʸ��������
    $data = "<h4>";
    if ($rowid) {
        $data .= "$rowid.";
    }
    $data .= "$ent_title$ent_created_on�ؤΎ��Ҏݎ����</h4><hr>";
    if ($mt->version_number() >= 3.0 && $cfg{ApproveComment} eq 'no') {
        $data .= "���ҎݎĤ���Ƹ塢�Ǻܤ���α����ޤ���<br>�����ͤˤ�뾵���塢�Ǻܤ���ޤ���<br>";
    }
    $data .= $cfg{CommentNotes};
    my $href;
    if ($mode eq 'postform') {
        $href = &make_href("post", 0, 0, $eid, 0);
    } elsif ($mode eq 'postform_rcm') {
        $href = &make_href("post_rcm", 0, 0, $eid, 0);
    } elsif ($mode eq 'postform_lnk') {
        $href = &make_href("post_lnk", 0, 0, $eid, 0);
    }
    $data .= "<form method=post action=\"$href\">";
    $data .= "̾��";
    if ($cfg{PostFromEssential} ne "yes"){
        $data .= "(��ά��)";
    } else {
        $data .= '(����ɬ��)';
    }
    $data .= "<br><input type=text name=from><br>";
    $data .= "�Ҏ��َ��Ďގڎ�";
    if ($cfg{PostMailEssential} ne "yes"){
        $data .= "(��ά��)";
    } else {
        $data .= '(����ɬ��)';
    }
    $data .= "<br><input type=text name=mail><br>";
    $data .= "���Ҏݎ�";
    if ($cfg{PostTextEssential} ne "yes"){
        $data .= "(��ά��)";
    } else {
        $data .= '(����ɬ��)';
    }
    $data .= "<br><textarea rows=4 name=text></textarea><br>";
    $data .= "<input type=hidden name=id value=$cfg{Blog_ID}>";
    if ($mode eq 'postform') {
        $data .= "<input type=hidden name=mode value=post>";
    } elsif ($mode eq 'postform_rcm') {
        $data .= "<input type=hidden name=mode value=post_rcm>";
    } elsif ($mode eq 'postform_lnk') {
        $data .= "<input type=hidden name=mode value=post_lnk>";
    }
    $data .= "�������פ򲡤��Ƥ���񤭹��ߴ�λ�ޤ�¿�����֤�������ޤ���<br>�Ķ��ˤ�äƤώ����ю����Ĥ��Ф뤳�Ȥ�����ޤ������񤭹��ߤϴ�λ���Ƥ��ޤ���<br>�������פ����ٲ��������Фˤ��ʤ��ǲ�������<br>";
    $data .= "<input type=hidden name=no value=$rowid>";
    $data .= "<input type=hidden name=eid value=$eid>";
    if ($key){
        $data .= "<input type=hidden name=\"key\" value=\"$key\">";
    }
    $data .= "<input type=submit value='����'>";
    $data .= "</form>";
    $data .= "<hr>";
    if ($mode eq 'postform') {
        $href = &make_href("individual", $rowid, 0, $eid, 0);
    } elsif ($mode eq 'postform_rcm') {
        $href = &make_href("individual_rcm", $rowid, 0, $eid, 0);
    } elsif ($mode eq 'postform_lnk') {
        $href = &make_href("individual_lnk", $rowid, 0, $eid, 0);
    }
    $data .="$nostr[0]<a href='$href'$akstr[0]>���</a>";
    &htmlout;
}

########################################
# Sub Post - ���������->ɽ������
########################################
sub post {
    require MT::Comment;
    require MT::App;

    # SPAM�к�
    # ��ʸ�����ꤷ���ѥ������Ŭ�礷�������Ȥ��Ƥ�
    my @comment_filter_strs = split(",", $cfg{CommentFilterStr});
    my $temp_post_text;
    if ($ecd == 1) {
        $temp_post_text = Encode::decode('shiftjis', $post_text);
    } else {
        $temp_post_text = Jcode->new($post_text,'sjis');
    }
    foreach my $comment_filter_str (@comment_filter_strs) {
        if ($temp_post_text =~ /$comment_filter_str/i) {
            print "Content-type: text/plain;\n\n";
            print "Block!";
            exit;
        }
    }

    my $rowid = $no;
    $no--;
    
    # ������Ƥ��öEUC-JP���Ѵ�
    if ($ecd == 1) {
        $post_from = encode("euc-jp",decode("shiftjis",$post_from));
        $post_text = encode("euc-jp",decode("shiftjis",$post_text));
    } else {
        $post_from = Jcode->new($post_from, 'sjis')->euc;
        $post_text = Jcode->new($post_text, 'sjis')->euc;
    }
    
    ####################
    # admin_helper������å�(�����ԥ⡼�ɻ��Τ�)
    my $post_from_org = $post_from;
    if (($cfg{AdminHelper} eq 'yes') && ($admin_mode eq 'yes')){
        if ($post_from_org eq $cfg{AdminHelperID}){
            $post_from = $cfg{AdminHelperNM};
            $post_mail = $cfg{AdminHelperML};
        }
    }
    
    ####################
    # ɬ�����Ϲ��ܤ�����å�
    # ̾��,mail,text�Τɤ�����Ϥ�̵����Х��顼
    if(((!$post_from)&&(!$post_text)&&(!$post_mail))||
       ((!$post_from)&&($cfg{PostFromEssential} eq "yes"))||
       ((!$post_mail)&&($cfg{PostMailEssential} eq "yes"))||
       ((!$post_text)&&($cfg{PostTextEssential} eq "yes")))
    {
        $data .="Error!<br>̤���Ϲ��ܤ�����ޤ�.<br>";
        my $href = &make_href("postform", $rowid, 0, $eid, 0);
        $data .="$nostr[0]<a href='$href'$akstr[0]>���</a>";
        &errorout;
        #return;
        exit;
    }
    
    ####################
    # �᡼�륢�ɥ쥹�����å�
    if ($post_mail){
        unless($post_mail=~/^[\w\-+\.]+\@[\w\-+\.]+$/i){
            $data .="Error!<br>�Ҏ��َ��Ďގڎ��������Ǥ�.<br>";
            my $href = &make_href("postform", $rowid, 0, $eid, 0);
            $data .="$nostr[0]<a href='$href'$akstr[0]>���</a>";
            &errorout;
            return;
        }
    }

    # ��Ƥ��줿ʸ�����Ⱦ�ѥ��ʤ����Ѥ��Ѵ�
    if ($ecd == 1) {
        Encode::JP::H2Z::h2z(\$post_from);
        Encode::JP::H2Z::h2z(\$post_text);
    } else {
        Jcode->new(\$post_from,'euc')->h2z;
        Jcode->new(\$post_text,'euc')->h2z;
    }

    # PublishCharset���Ѵ�
    if ($conv_in ne 'euc') {
        if ($conv_in eq 'utf8' && $ecd == 1) {
            $post_from = encode("shiftjis",decode("euc-jp",$post_from));
            $post_text = encode("shiftjis",decode("euc-jp",$post_text));
            $post_from = encode("utf8",decode("cp932",$post_from));
            $post_text = encode("utf8",decode("cp932",$post_text));
        } else {
            $post_from = Jcode->new($post_from, 'euc')->$conv_in();
            $post_text = Jcode->new($post_text, 'euc')->$conv_in();
        }
    }
    
    # Ϣ³����ɻ�
    # ��ľ���Υ����Ȥ���Ӥ���Ʊ���ƤǤ����
    #   Ϣ³��ƤȤߤʤ����顼�Ȥ��롣
    #   ���դ���Ϣ³����ɻߤȤ������ϡ�
    #   �����ॢ���ȸ�ʤɤ��Ժ�٤βἺ�ɻߡ���
    my @comments = get_comments($eid, 1, 'descend', 0);
    
    for my $tmp (@comments) {
        if ($post_from eq $tmp->author &&
            $post_mail eq $tmp->email &&
            $post_text eq $tmp->text) {
            $data .="Error!<br>Ʊ���ƤΎ��ҎݎĤ�������Ƥ���Ƥ��ޤ�<hr>";
            my $href = &make_href("comment", $rowid, 0, $eid, 0);
            $data .="$nostr[0]<a href='$href'$akstr[0]>��Ƥ��줿���ҎݎĤ��ǧ����</a>";
            &errorout;
            return;
        }
    }
    
    # Entry ID��Entry Title�μ���
    require MT::Entry;
    my $entry = MT::Entry->load($eid);

    # ������̤�0��ξ��ϥ�å�����ɽ������STOP��ͭ�����ʤ����ɤʡ�
    if ($entry <= 0) {
        if ($hentities == 1) {
            $data = 'Entry ID \''.encode_entities($eid).'\' �������Ǥ���';
        } else {
            $data = 'Entry ID \''.$eid.'\' �������Ǥ���';
        }
        &errorout;
        exit;      # exit����
    }

    # DB����
    my $comment = MT::Comment->new;
    my $rm_ip = $ENV{'REMOTE_ADDR'};
    $comment->ip($rm_ip);
    $comment->blog_id($cfg{Blog_ID});
    $comment->entry_id($entry->id);
    $comment->author($post_from);
    $comment->email($post_mail);
    $comment->text($post_text);
    #if ($admin_data[3]){
    #    $comment->url($admin_data[3]);
    #}
    
    # MT3.0�ʾ�ʤ�visible������
    if ($mt->version_number() >= 3.0) {
        # $cfg{ApproveComment}='yes'�ξ��ˤϡ��񤭹��ߤ�Ʊ���˷Ǻܤ�������
        if ($cfg{ApproveComment} eq 'yes') {
            $comment->visible(1);
        } else {
            $comment->visible(0);
        }
    }
    
    $comment->save
        or die $comment->errstr;

    ####################
    # MT3.0�ʾ�Ǥϡ����Υ᡼�������ڤӥ�ӥ�ɤ�Хå����饦��ɤǹԤ�
    if ($mt->version_number() >= 3.0) {
        require MT::Util;
        MT::Util::start_background_task(sub {
            # �᡼������
            if ($blog->email_new_comments) {
                require MT::Mail;
                my $author = $entry->author;
                $mt->set_language($author->preferred_language)
                    if $author && $author->preferred_language;
                if ($author && $author->email) {
                    my %head = (    To => $author->email,
                                    From => $comment->email || $author->email,
                                    Subject =>
                                        '[' . $blog->name . '] ' .
                                        $entry->title . &conv_euc2icode(' �ؤο����������� from MT4i')
                                );
                    my $charset;
                    # MT3.3�ʹߤ�ư����Ѥ���
                    if ($mt->version_number() >= 3.3) {
                        $charset = $mt->{cfg}->MailEncoding || $mt->{cfg}->PublishCharset;
                    } else {
                        $charset = $mt->{cfg}->PublishCharset || 'iso-8859-1';
                    }
                    $head{'Content-Type'} = qq(text/plain; charset="$charset");
                    my $body = &conv_euc2icode('�����������Ȥ������֥� ') .
                                $blog->name  . ' ' .
                                &conv_euc2icode('�Υ���ȥ꡼ #') . $entry->id . " (" .
                                $entry->title . &conv_euc2icode(') �ˤ���ޤ���');
                    
                    # �������ؤΥ�󥯺���
                    my $link_url = $entry->permalink;
                    
                    use Text::Wrap;
                    $Text::Wrap::cols = 72;
                    $body = Text::Wrap::wrap('', '', $body) . "\n$link_url\n\n" .
                    $body = $body . "\n$link_url\n\n" .
                      &conv_euc2icode('IP���ɥ쥹:') . ' ' . $comment->ip . "\n" .
                      &conv_euc2icode('̾��:') . ' ' . $comment->author . "\n" .
                      &conv_euc2icode('�᡼�륢�ɥ쥹:') . ' ' . $comment->email . "\n" .
                      &conv_euc2icode('URL:') . ' ' . $comment->url . "\n\n" .
                      &conv_euc2icode('������:') . "\n\n" . $comment->text . "\n\n" .
                      &conv_euc2icode("-- \nfrom MT4i v$version\n");
                    MT::Mail->send(\%head, $body);
                }
            }

            ####################
            # ��ӥ��
            
            # Index�ƥ�ץ졼��
            if ($cfg{RIT_ID} eq 'ALL') {
                $mt->rebuild_indexes( BlogID => $cfg{Blog_ID} )
                    or die $mt->errstr;
            } else {
                my @tmp_RIT_ID = split(",", $cfg{RIT_ID});
                foreach my $indx_tmpl_id (@tmp_RIT_ID) {
                    require MT::Template;
                    my $tmpl_saved = MT::Template->load($indx_tmpl_id);
                    $mt->rebuild_indexes( BlogID => $cfg{Blog_ID}, Template => $tmpl_saved, Force => 1 )
                        or die $mt->errstr;
                }
            }
            
            # Archive�ƥ�ץ졼��
            if ($cfg{RAT_ID} eq 'ALL') {
                $mt->rebuild_entry( Entry => $entry )
                    or die $mt->errstr;
            } else {
                my @tmp_RAT_ID = split(",", $cfg{RAT_ID});
                foreach my $arc_tmpl_id (@tmp_RAT_ID) {
                    $mt->publisher->_rebuild_entry_archive_type(
                        Entry => $entry,
                        Blog => $blog,
                        ArchiveType => $arc_tmpl_id
                        )
                        or die $mt->errstr;
                }
            }
        });
    } else {
        # �᡼������
        if ($blog->email_new_comments) {
            require MT::Mail;
            my $author = $entry->author;
            $mt->set_language($author->preferred_language)
                if $author && $author->preferred_language;
            if ($author && $author->email) {
                my %head = (    To => $author->email,
                                From => $comment->email || $author->email,
                                Subject =>
                                    '[' . $blog->name . '] ' .
                                    $entry->title . &conv_euc2icode(' �ؤο����������� from MT4i')
                           );
                my $charset = $mt->{cfg}->PublishCharset || 'iso-8859-1';
                $head{'Content-Type'} = qq(text/plain; charset="$charset");
                my $body = &conv_euc2icode('�����������Ȥ������֥� ') .
                            $blog->name  . ' ' .
                            &conv_euc2icode('�Υ���ȥ꡼ #') . $entry->id . " (" .
                            $entry->title . &conv_euc2icode(') �ˤ���ޤ���');
                
                # �������ؤΥ�󥯺���
                my $link_url = $entry->permalink;
                
                use Text::Wrap;
                $Text::Wrap::cols = 72;
                $body = Text::Wrap::wrap('', '', $body) . "\n$link_url\n\n" .
                $body = $body . "\n$link_url\n\n" .
                  &conv_euc2icode('IP���ɥ쥹:') . ' ' . $comment->ip . "\n" .
                  &conv_euc2icode('̾��:') . ' ' . $comment->author . "\n" .
                  &conv_euc2icode('�᡼�륢�ɥ쥹:') . ' ' . $comment->email . "\n" .
                  &conv_euc2icode('URL:') . ' ' . $comment->url . "\n\n" .
                  &conv_euc2icode('������:') . "\n\n" . $comment->text . "\n\n" .
                  &conv_euc2icode("-- \nfrom MT4i v$version\n");
                MT::Mail->send(\%head, $body);
            }
        }

        ####################
        # ��ӥ��
        
        # Index�ƥ�ץ졼��
        if ($cfg{RIT_ID} eq 'ALL') {
            $mt->rebuild_indexes( BlogID => $cfg{Blog_ID} )
                or die $mt->errstr;
        } else {
            my @tmp_RIT_ID = split(",", $cfg{RIT_ID});
            foreach my $indx_tmpl_id (@tmp_RIT_ID) {
                require MT::Template;
                my $tmpl_saved = MT::Template->load($indx_tmpl_id);
                $mt->rebuild_indexes( BlogID => $cfg{Blog_ID}, Template => $tmpl_saved, Force => 1 )
                    or die $mt->errstr;
            }
        }
        
        # Archive�ƥ�ץ졼��
        if ($cfg{RAT_ID} eq 'ALL') {
            $mt->rebuild_entry( Entry => $entry )
                or die $mt->errstr;
        } else {
            my @tmp_RAT_ID = split(",", $cfg{RAT_ID});
            foreach my $arc_tmpl_id (@tmp_RAT_ID) {
                $mt->_rebuild_entry_archive_type( Entry => $entry,
                                                  Blog => $blog,
                                                  ArchiveType => $arc_tmpl_id )
                    or die $mt->errstr;
            }
        }
    }

    # ����ɽ��
    if ($mt->version_number() >= 3.0 && $cfg{ApproveComment} eq 'no') {
        $data = "���ҎݎĤ���Ƥ���ޤ��������Ǻܤ���α����Ƥ��ޤ���<br>�����ͤˤ�뾵���塢�Ǻܤ���ޤ���<hr>";
    } else {
        $data = "���ҎݎĤ���Ƥ���ޤ���<hr>";
    }
    my $href;
    if ($mode eq 'post') {
        $href = &make_href("comment", $rowid, 0, $eid, 0);
    } elsif ($mode eq 'post_rcm') {
        $href = &make_href("comment_rcm", $rowid, 0, $eid, 0);
    } elsif ($mode eq 'post_lnk') {
        $href = &make_href("comment_lnk", $rowid, 0, $eid, 0);
    }
    $data .="$nostr[0]<a href='$href'$akstr[0]>���</a>";
    &htmlout;
}

########################################
# Sub entryform - ����Entry/Entry�Խ� �ե�����
########################################
sub entryform {
    
    my ($org_title,
        $org_text,
        $org_text_more,
        $org_excerpt,
        $org_keywords,
        $org_tags,
        $org_convert_breaks,
        $org_created_on,
        $org_authored_on,
        $org_comment_cnt,
        $org_ent_status,
        $org_ent_allow_comments,
        $org_ent_allow_pings
    );
    my $rowid = $no;
    
    if ($eid == 0){
        $data = "<h4>����Entry�κ���</h4><hr>";
        
        # ���������μ���
        $ENV{TZ} = 'JST-9';
        my $time = time;
        my ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($time);
        $mon++;
        $year = 1900+$year;
        $mon = sprintf("%.2d",$mon);
        $mday = sprintf("%.2d",$mday);
        $hour = sprintf("%.2d",$hour);
        $sec = sprintf("%.2d",$sec);
        $min = sprintf("%.2d",$min);
        if ($mt->version_number >= 4.0) {
            $org_authored_on = "$year-$mon-$mday $hour:$min:$sec";
        } else {
            $org_created_on = "$year-$mon-$mday $hour:$min:$sec";
        }
    }else{
        
        $data = "<h4>Entry���Խ�</h4><hr>";
        
        # Entry����
        require MT::Entry;
        my $entry = MT::Entry->load($eid);
        
        # ������̤�0��ξ��ϥ�å�����ɽ������STOP��ͭ�����ʤ����ɤʡ�
        if (!$entry) {
            if ($hentities == 1) {
                $data = 'Entry ID \''.encode_entities($eid).'\' �������Ǥ���';
            } else {
                $data = 'Entry ID \''.$eid.'\' �������Ǥ���';
            }
            &errorout;
            exit;      # exit����
        }
        
        # �Խ��ʤΤǡ����Υǡ���������
        $org_title = &conv_euc_z2h($entry->title);
        $org_text = &conv_euc_z2h($entry->text);
        $org_text_more = &conv_euc_z2h($entry->text_more);
        $org_excerpt = &conv_euc_z2h($entry->excerpt);
        $org_keywords = &conv_euc_z2h($entry->keywords);
        if ($mt->version_number() >= 3.3) {
            require MT::Author;
            # AuthorName��PublishCharset���Ѵ�
            if ($conv_in ne 'euc') {
                if ($conv_in eq 'utf8' && $ecd == 1) {
                    $cfg{AuthorName} = encode("shiftjis",decode("euc-jp",$cfg{AuthorName}));
                    $cfg{AuthorName} = encode("utf8",decode("cp932",$cfg{AuthorName}));
                } else {
                    $cfg{AuthorName} = Jcode->new($cfg{AuthorName}, 'euc')->$conv_in();
                }
            }
            my $author = MT::Author->load({ name => $cfg{AuthorName} });
            my $tag_delim = chr($author->entry_prefs->{tag_delim});
            require MT::Tag;
            my $tags = MT::Tag->join($tag_delim, $entry->tags);
            $org_tags = &conv_euc_z2h($tags);
        }
        $org_convert_breaks = $entry->convert_breaks;
        if ($mt->version_number >= 4.0) {
            $org_authored_on = $entry->created_on;
            $org_authored_on =~ s/(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)/$1-$2-$3 $4:$5:$6/;
        } else {
            $org_created_on = $entry->created_on;
            $org_created_on =~ s/(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)/$1-$2-$3 $4:$5:$6/;
        }
        $org_comment_cnt = $entry->comment_count;
        $org_ent_status = $entry->status;
        $org_ent_allow_comments = $entry->allow_comments;
        $org_ent_allow_pings = $entry->allow_pings;
        
        # �����ȥ�򥨥󥳡���
        $org_title =~ s/&/&amp;/g;
        $org_title =~ s/ /&nbsp;/g;
        $org_title =~ s/\</&lt;/g;
        $org_title =~ s/\>/&gt;/g;
        # ��ʸ�򥨥󥳡���
        $org_text =~ s/&/&amp;/g;
        $org_text =~ s/\</&lt;/g;
        $org_text =~ s/\>/&gt;/g;
        # �ɵ��򥨥󥳡���
        $org_text_more =~ s/&/&amp;/g;
        $org_text_more =~ s/\</&lt;/g;
        $org_text_more =~ s/\>/&gt;/g;
        # ���פ򥨥󥳡���
        $org_excerpt =~ s/&/&amp;/g;
        $org_excerpt =~ s/\</&lt;/g;
        $org_excerpt =~ s/\>/&gt;/g;
        # ������ɤ򥨥󥳡���
        $org_keywords =~ s/&/&amp;/g;
        $org_keywords =~ s/\</&lt;/g;
        $org_keywords =~ s/\>/&gt;/g;
        # �����򥨥󥳡���
        $org_tags =~ s/&/&amp;/g;
        $org_tags =~ s/ /&nbsp;/g;
        $org_tags =~ s/\</&lt;/g;
        $org_tags =~ s/\>/&gt;/g;
    }
    
    ####################
    # ɽ��ʸ��������
    my $href = &make_href("post", 0, 0, $eid, 0);
    $data .= "<form method=\"post\" action=\"$href\">";
    
    # ���ƥ��ꥻ�쥯��
    my $cat_label;
    if ($eid){
        $cat_label = &check_category(MT::Entry->load($eid));
    }
    $data .= "���Î��ގ�<br>";
    $data .= "<select name=\"entry_cat\">";
    $data .= "<option value=0>";
    require MT::Category;
    my @categories = MT::Category->load({blog_id => $cfg{Blog_ID}},
                                            {unique => 1});
    for my $category (@categories) {
        my $label;
        if ($cfg{CatDescReplace} eq "yes"){
            $label = &conv_euc_z2h($category->description);
        }else{
            $label = &conv_euc_z2h($category->label);
        }
        my $cat_id = $category->id;
        
        if ($cat_label eq $label){
            $data .= "<option value=$cat_id selected>$label<br>";
        }else{
            $data .= "<option value=$cat_id>$label<br>";
        }
    }
    $data .= "</select><br>";
    
    $data .= "�����Ď�";
    $data .= "<br><input type=\"text\" name=\"entry_title\" value=\"$org_title\"><br>";
    $data .= "Entry������";
    $data .= "<br><textarea rows=\"4\" name=\"entry_text\">$org_text</textarea><br>";
    $data .= "Extended(�ɵ�)";
    $data .= "<br><textarea rows=\"4\" name=\"entry_text_more\">$org_text_more</textarea><br>";
    $data .= "Excerpt(����)";
    $data .= "<br><textarea rows=\"4\" name=\"entry_excerpt\">$org_excerpt</textarea><br>";
    $data .= "�����܎��Ď�";
    $data .= "<br><textarea rows=\"4\" name=\"entry_keywords\">$org_keywords</textarea><br>";
    if ($mt->version_number() >= 3.3) {
        $data .= "������(���ݎϤǶ��ڤ�)";
        $data .= "<br><input type=\"text\" name=\"entry_tags\" value=\"$org_tags\"><br>";
    }
    $data .= "��Ƥξ���<br>";
    $data .= "<select name=\"post_status\">";
    if (($eid && $org_ent_status == 1) || (!$eid && $blog->status_default == 1)) {
        $data .= "<option value=1 selected>����<br>";
        $data .= "<option value=2>����<br>";
        if ($mt->version_number() >= 3.1) {
            $data .= "<option value=3>������<br>";
        }
    } elsif (($eid && $org_ent_status == 2) || (!$eid && $blog->status_default == 2)) {
        $data .= "<option value=1>����<br>";
        $data .= "<option value=2 selected>����<br>";
        if ($mt->version_number() >= 3.1) {
            $data .= "<option value=3>������<br>";
        }
    } elsif (($eid && $org_ent_status == 3)) {
        $data .= "<option value=1>����<br>";
        $data .= "<option value=2>����<br>";
        if ($mt->version_number() >= 3.1) {
            $data .= "<option value=3 selected>������<br>";
        }
    } else {
        $data .= "<option value=1>����<br>";
        $data .= "<option value=2 selected>����<br>";
        if ($mt->version_number() >= 3.1) {
            $data .= "<option value=3>������<br>";
        }
    }
    $data .= "</select><br>";
    $data .= "<input type=\"hidden\" name=\"post_status_old\" value=\"".$org_ent_status."\">";
    
    $data .= "���Ҏݎ�<br>";
    $data .= "<select name=\"allow_comments\">";
    
    if (($eid && $org_ent_allow_comments == 0) || (!$eid && $blog->allow_comments_default == 0)) {
            $data .= "<option value=0 selected>�ʤ�<br>";
            $data .= "<option value=1>�����̎ߎ�<br>";
            $data .= "<option value=2>���ێ�����<br>";
    } elsif (($eid && $org_ent_allow_comments == 1) || (!$eid && $blog->allow_comments_default == 1)) {
            $data .= "<option value=0>�ʤ�<br>";
            $data .= "<option value=1 selected>�����̎ߎ�<br>";
            $data .= "<option value=2>���ێ�����<br>";
    } else {
            $data .= "<option value=0>�ʤ�<br>";
            $data .= "<option value=1>�����̎ߎ�<br>";
            $data .= "<option value=2 selected>���ێ�����<br>";
    }
    $data .= "</select><br>";
    
    $data .= "�Ď׎����ʎގ���������Ĥ���<br>";
    if (($eid && $org_ent_allow_pings) || (!$eid && $blog->allow_pings_default == 1)) {
        $data .= "<INPUT TYPE=checkbox name=\"allow_pings\" value=\"1\" CHECKED><br>";
    }else{
        $data .= "<INPUT TYPE=checkbox name=\"allow_pings\" value=\"1\"><br>";
    }
    
    ## �ƥ����ȥե����ޥåȤΥ���
    my $filters = $mt->all_text_filters;
    my $text_filters = [];
    for my $filter (keys %$filters) {
        my $label = $filters->{$filter}{label};
        if ($mt->version_number() >= 4.0) {
            $label = $label->() if ref($label) eq 'CODE';
        }
        push @{ $text_filters }, {
            filter_key => $filter,
            filter_label => &conv_euc_z2h($label),
        };
    }
    # ������
    $text_filters = [ sort { $a->{filter_key} cmp $b->{filter_key} } @{ $text_filters } ];
    # �֤ʤ��פ��ɲ�
    unshift @{ $text_filters }, {
        filter_key => '0',
        filter_label => '�ʤ�',
    };
    # ����
    $data .= "�Î����Ď̎����ώ���<br>";
    $data .= '<select name="convert_breaks">';
    foreach my $filter ( @{ $text_filters } ) {
        my $selected;
        if (($org_convert_breaks eq $filter->{filter_key}) || (!$org_convert_breaks && $convert_paras eq $filter->{filter_key})) {
            $selected = ' selected';
        }
        $data .= "<option value=\"$filter->{filter_key}\"$selected>$filter->{filter_label}";
    }
    $data .= '</select><br>';
    
    if ($mt->version_number() >= 4.0) {
        $data .= "��������<br>";
        $data .= "<input type=\"text\" name=\"entry_authored_on\" value=\"$org_authored_on\"><br>";
    } else {
        $data .= "��������<br>";
        $data .= "<input type=\"text\" name=\"entry_created_on\" value=\"$org_created_on\"><br>";
    }
    
    $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
    $data .= "<input type=\"hidden\" name=\"mode\" value=\"entry\">";
    $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
    $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
    if ($key){
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
    }
    $data .= "<input type=\"submit\" value=\"����\">";
    $data .= "</form>";
    $data .= "<hr>";
    $href = &make_href("", 0, 0, 0, 0);
    $data .= "$nostr[0]<a href='$href'$akstr[0]>���������</a>";
    &htmlout;
}

########################################
# Sub Entry - ����Entry���->ɽ������
########################################
sub entry {
    my $rowid = $no;
    $no--;
    
    # ������Ƥ��öEUC-JP���Ѵ�
    if ($ecd == 1) {
        $entry_title = encode("euc-jp",decode("shiftjis",$entry_title));
        $entry_text = encode("euc-jp",decode("shiftjis",$entry_text));
        $entry_text_more = encode("euc-jp",decode("shiftjis",$entry_text_more));
        $entry_excerpt = encode("euc-jp",decode("shiftjis",$entry_excerpt));
        $entry_keywords = encode("euc-jp",decode("shiftjis",$entry_keywords));
        $entry_tags = encode("euc-jp",decode("shiftjis",$entry_tags));
    } else {
        $entry_title = Jcode->new($entry_title, 'sjis')->euc;
        $entry_text = Jcode->new($entry_text, 'sjis')->euc;
        $entry_text_more = Jcode->new($entry_text_more, 'sjis')->euc;
        $entry_excerpt = Jcode->new($entry_excerpt, 'sjis')->euc;
        $entry_keywords = Jcode->new($entry_keywords, 'sjis')->euc;
        $entry_tags = Jcode->new($entry_tags, 'sjis')->euc;
    }
    
    # Ⱦ�ѥ��ڡ���'&nbsp;'��ǥ�����
    $entry_title =~ s/&nbsp;/ /g;
    $entry_tags =~ s/&nbsp;/ /g;

    ####################
    # ɬ�����Ϲ��ܤ�����å�
    # �����ȥ롢�ƥ����ȤΤɤ��餫�����Ϥ�̵����Х��顼
    if((!$entry_title)||(!$entry_text))
    {
        $data .="Error!<br>̤���Ϲ��ܤ�����ޤ����֎����Ď١פȡ�Entry�����ơפ�ɬ�ܤǤ���<br>";
        my $href = &make_href("entryform", 0, 0, $eid, 0);
        $data .="$nostr[0]<a href=\"$href\"$akstr[0]>���</a>";
        &errorout;
        return;
    }
    # �����������뤤�ϸ������������Ϥ�̵����Х��顼
    if ($mt->version_number() >= 4.0) {
        if (!$entry_authored_on) {
            $data .="Error!<br>̤���Ϲ��ܤ�����ޤ����ָ��������פ�ɬ�ܤǤ���<br>";
            my $href = &make_href("entryform", 0, 0, $eid, 0);
            $data .="$nostr[0]<a href=\"$href\"$akstr[0]>���</a>";
            &errorout;
            return;
        }
    } else {
        if (!$entry_created_on) {
            $data .="Error!<br>̤���Ϲ��ܤ�����ޤ����ֺ��������פ�ɬ�ܤǤ���<br>";
            my $href = &make_href("entryform", 0, 0, $eid, 0);
            $data .="$nostr[0]<a href=\"$href\"$akstr[0]>���</a>";
            &errorout;
            return;
        }
    }
    require MT::Author;
    # AuthorName��PublishCharset���Ѵ�
    if ($conv_in ne 'euc') {
        if ($conv_in eq 'utf8' && $ecd == 1) {
            $cfg{AuthorName} = encode("shiftjis",decode("euc-jp",$cfg{AuthorName}));
            $cfg{AuthorName} = encode("utf8",decode("cp932",$cfg{AuthorName}));
        } else {
            $cfg{AuthorName} = Jcode->new($cfg{AuthorName}, 'euc')->$conv_in();
        }
    }
    if (!$cfg{AuthorName}) {
        $data = 'MT4i Manager �ˤ� Author̾��AuthorName�ˤ����ꤵ��Ƥ��ޤ���';
        &errorout;
        exit;      # exit����
    }
    my $author = MT::Author->load({ name => $cfg{AuthorName} });
    if (!$author) {
        # AuthorName��EUC-JP���᤹
        if ($conv_in eq 'utf8' && $ecd == 1) {
            $cfg{AuthorName} = encode("cp932",decode("utf8",$cfg{AuthorName}));
            $cfg{AuthorName} = encode("euc-jp",decode("shiftjis",$cfg{AuthorName}));
        } else {
            $cfg{AuthorName} = Jcode->new($cfg{AuthorName}, $conv_in)->euc;
        }
        $data = "\"$cfg{AuthorName}\"��Author�Ȥ�����Ͽ����Ƥ��ޤ���<br>";
        &errorout;
        exit;      # exit����
    }
    
    # ��Ƥ��줿ʸ�����Ⱦ�ѥ��ʤ����Ѥ��Ѵ�
    if ($ecd == 1) {
        Encode::JP::H2Z::h2z(\$entry_title);
        Encode::JP::H2Z::h2z(\$entry_text);
        Encode::JP::H2Z::h2z(\$entry_text_more);
        Encode::JP::H2Z::h2z(\$entry_excerpt);
        Encode::JP::H2Z::h2z(\$entry_keywords);
        Encode::JP::H2Z::h2z(\$entry_tags);
    } else {
        Jcode->new(\$entry_title, 'euc')->h2z;
        Jcode->new(\$entry_text, 'euc')->h2z;
        Jcode->new(\$entry_text_more, 'euc')->h2z;
        Jcode->new(\$entry_excerpt, 'euc')->h2z;
        Jcode->new(\$entry_keywords, 'euc')->h2z;
        Jcode->new(\$entry_tags, 'euc')->h2z;
    }
    # PublishCharset���Ѵ�
    if ($conv_in ne 'euc') {
        if ($conv_in eq 'utf8' && $ecd == 1) {
            $entry_title = encode("shiftjis",decode("euc-jp",$entry_title));
            $entry_text = encode("shiftjis",decode("euc-jp",$entry_text));
            $entry_text_more = encode("shiftjis",decode("euc-jp",$entry_text_more));
            $entry_excerpt = encode("shiftjis",decode("euc-jp",$entry_excerpt));
            $entry_keywords = encode("shiftjis",decode("euc-jp",$entry_keywords));
            $entry_tags = encode("shiftjis",decode("euc-jp",$entry_tags));
            $entry_title = encode("utf8",decode("cp932",$entry_title));
            $entry_text = encode("utf8",decode("cp932",$entry_text));
            $entry_text_more = encode("utf8",decode("cp932",$entry_text_more));
            $entry_excerpt = encode("utf8",decode("cp932",$entry_excerpt));
            $entry_keywords = encode("utf8",decode("cp932",$entry_keywords));
            $entry_tags = encode("utf8",decode("cp932",$entry_tags));
        } else {
            $entry_title = Jcode->new($entry_title, 'euc')->$conv_in();
            $entry_text = Jcode->new($entry_text, 'euc')->$conv_in();
            $entry_text_more = Jcode->new($entry_text_more, 'euc')->$conv_in();
            $entry_excerpt = Jcode->new($entry_excerpt, 'euc')->$conv_in();
            $entry_keywords = Jcode->new($entry_keywords, 'euc')->$conv_in();
            $entry_tags = Jcode->new($entry_tags, 'euc')->$conv_in();
        }
    }
    
    require MT::Entry;
    my $entry;
    if ($eid){
        $entry = MT::Entry->load($eid);
    }else{
        $entry = MT::Entry->new;
    }
    $entry->blog_id($blog->id);
    $entry->status($post_status);
    $entry->author_id($author->id);
    $entry->title($entry_title);
    $entry->text($entry_text);
    $entry->text_more($entry_text_more);
    $entry->excerpt($entry_excerpt);
    $entry->keywords($entry_keywords);
    if ($mt->version_number() >= 3.3) {
        my $tag_delim = chr($author->entry_prefs->{tag_delim});
        require MT::Tag;
        my @tags = MT::Tag->split($tag_delim, $entry_tags);
        $entry->add_tags(@tags);
    }
    if ($allow_pings == 1){
        $entry->allow_pings(1);
    }else{
        $entry->allow_pings(0);
    }
    $entry->allow_comments($allow_comments);
    $entry->convert_breaks($text_format);
    if ($mt->version_number() >= 4.0) {
        $entry_authored_on =~ s/(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)/$1$2$3$4$5$6/;
        $entry->authored_on($entry_authored_on);
    } else {
        $entry_created_on =~ s/(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)/$1$2$3$4$5$6/;
        $entry->created_on($entry_created_on);
    }
    $entry->save
        or die $entry->errstr;
    
    if ($entry_cat) {
        require MT::Placement;
        my $place = MT::Placement->load({ blog_id => $cfg{Blog_ID} , entry_id => $entry->id });
        
        if (!$place){
            $place = MT::Placement->new;
        }
        $place->entry_id($entry->id);
        $place->blog_id($cfg{Blog_ID});
        $place->category_id($entry_cat);
        $place->is_primary(1);
        $place->save
            or die $place->errstr;
    }
    if ($eid){
        $data = "Entry�Ͻ�������ޤ���<hr>";
    }else{
        $data = "����Entry����������ޤ���<hr>";
    }
    
    ####################
    # ��¸�Υ��ơ���������꡼���������뤤���Խ����Υ��ơ���������꡼���ξ��Τ�
    # ����ȥ꡼�ڤӥ���ǥå����Υ�ӥ�ɤ�Ԥ����ԥ󥰤��������롣
    if ($post_status == MT::Entry::RELEASE() || $post_status_old eq MT::Entry::RELEASE()) {
        # MT3.0�ʾ�Ǥϡ���ӥ�ɵڤӹ���ping������Хå����饦��ɤǹԤ�
        if ($mt->version_number() >= 3.0) {
            require MT::Util;
            MT::Util::start_background_task(sub {
                # ��ӥ��
                $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                    or die $mt->errstr;
                
                ####################
                # ����ping����
                # ��¸�Υ��ơ���������꡼���ξ��Τ�ping����
                if ($post_status == MT::Entry::RELEASE() || $post_status_old eq MT::Entry::RELEASE()) {
                    require MT::XMLRPC;
                    if ($blog->ping_others){
                        my (@updateping_urls) = split(/\n/,$blog->ping_others);
                        for my $url (@updateping_urls) {
                            MT::XMLRPC->ping_update('weblogUpdates.ping', $blog,
                                $url)
                                or die MT::XMLRPC->errstr;
                        }
                    }
                }
            });
        } else {
            # ��ӥ��
            $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                or die $mt->errstr;
            
            ####################
            # ����ping����
            # ��¸�Υ��ơ���������꡼���ξ��Τ�ping����
            if ($post_status == MT::Entry::RELEASE()){
                require MT::XMLRPC;
                if ($blog->ping_others){
                    my (@updateping_urls) = split(/\n/,$blog->ping_others);
                    for my $url (@updateping_urls) {
                        MT::XMLRPC->ping_update('weblogUpdates.ping', $blog,
                            $url)
                            or die MT::XMLRPC->errstr;
                    }
                }
            }
        }
    }
    my $href = &make_href("", 0, 0, 0, 0);
    $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>���������</a>";
    &htmlout;
}

########################################
# Sub Entry_del - Entry���
########################################
sub entry_del {
    
    my $rowid = $no;
    $no--;
    
    require MT::Entry;
    my $entry = MT::Entry->load($eid);
    if (!$entry) {
        if ($hentities == 1) {
            $data = 'entry_del::Entry ID \''.encode_entities($eid).'\' �������Ǥ���';
        } else {
            $data = 'entry_del::Entry ID \''.$eid.'\' �������Ǥ���';
        }
        &errorout;
        exit;      # exit����
    }
    
    $entry->remove;
    
    ####################
    # MT3.0�ʾ�Ǥϡ���ӥ�ɤ�Хå����饦��ɤǹԤ�
    if ($mt->version_number() >= 3.0) {
        require MT::Util;
        MT::Util::start_background_task(sub {
            # ��ӥ��
            #$mt->rebuild_indexes( Blog => $blog )
            #    or die $mt->errstr;
            $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                or die $mt->errstr;
        });
    } else {
        # ��ӥ��
        #$mt->rebuild_indexes( Blog => $blog )
        #    or die $mt->errstr;
        $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
            or die $mt->errstr;
    }
    
    $data = "Entry���������ޤ���<hr>";
    my $href = &make_href("", 0, 0, 0, 0);
    $data .= "$nostr[0]<a href='$href'$akstr[0]>���������</a>";
    &htmlout;
}

########################################
# Sub Comment_del - �����Ⱥ��
########################################
sub comment_del {
    
    my $rowid = $no;
    $no--;
    
    ####################
    # comment��õ��
    require MT::Comment;
    my $comment = MT::Comment->load($page);    # �������ֹ��$page���Ϥ�
    if (!$comment) {
        if ($hentities == 1) {
            $data = "comment_del::Comment ID '".encode_entities($page)."' �������Ǥ���";
        } else {
            $data = "comment_del::Comment ID '".$page."' �������Ǥ���";
        }
        &errorout;
        exit;      # exit����
    }
    $comment->remove()
        or die $comment->errstr;
    
    #����comment��°����Entry��õ��
    require MT::Entry;
    my $entry = MT::Entry->load($comment->entry_id);
    if (!$entry) {
        $data = "comment_del::Entry ID '".$comment->entry_id."' �������Ǥ���";
        &errorout;
        exit;      # exit����
    }
    
    ####################
    # MT3.0�ʾ�Ǥϡ���ӥ�ɤ�Хå����饦��ɤǹԤ�
    if ($mt->version_number() >= 3.0) {
        require MT::Util;
        MT::Util::start_background_task(sub {
            # ��ӥ��
            #$mt->rebuild_indexes( Blog => $blog )
            #    or die $mt->errstr;
            $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                or die $mt->errstr;
        });
    } else {
        # ��ӥ��
        #$mt->rebuild_indexes( Blog => $blog )
        #    or die $mt->errstr;
        $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
            or die $mt->errstr;
    }
    
    $data = "���ҎݎĤ��������ޤ���<hr>";
    my $href = &make_href("comment", $rowid, 0, $eid, 0);
    $data .= "$nostr[0]<a href=\'$href\'$akstr[0]>���Ҏݎİ��������</a>";
    &htmlout;
}

########################################
# Sub Trackback_del - �ȥ�å��Хå����
########################################
sub trackback_del {
    
    my $rowid = $no;
    $no--;
    
    ####################
    # ping��õ��
    require MT::TBPing;
    my $tbping = MT::TBPing->load($page);    # �ȥ�å��Хå��ֹ��$page���Ϥ�
    if (!$tbping) {
        if ($hentities == 1) {
            $data = "trackback_del::MTPing ID '".encode_entities($page)."' �������Ǥ���";
        } else {
            $data = "trackback_del::MTPing ID '".$page."' �������Ǥ���";
        }
        &errorout;
        exit;      # exit����
    }
    $tbping->remove()
        or die $tbping->errstr;
    
    #����tbping��°����Trackback��õ��
    require MT::Trackback;
    my $trackback = MT::Trackback->load($tbping->tb_id);
    if (!$trackback) {
        $data = "trackback_del::Trackback ID '".$tbping->tb_id."' �������Ǥ���";
        &errorout;
        exit;      # exit����
    }
    
    #����Trackback��°����Entry��õ��
    require MT::Entry;
    my $entry = MT::Entry->load($trackback->entry_id);
    if (!$entry) {
        $data = "trackback_del::Entry ID '".$trackback->entry_id."' �������Ǥ���";
        &errorout;
        exit;      # exit����
    }
    
    ####################
    # MT3.0�ʾ�Ǥϡ���ӥ�ɤ�Хå����饦��ɤǹԤ�
    if ($mt->version_number() >= 3.0) {
        require MT::Util;
        MT::Util::start_background_task(sub {
            # ��ӥ��
            #$mt->rebuild_indexes( Blog => $blog )
            #    or die $mt->errstr;
            $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                or die $mt->errstr;
        });
    } else {
        # ��ӥ��
        #$mt->rebuild_indexes( Blog => $blog )
        #    or die $mt->errstr;
        $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
            or die $mt->errstr;
    }
    
    $data = "�Ď׎����ʎގ������������ޤ���<hr>";
    my $href = &make_href("trackback", $rowid, 0, $eid, 0);
    $data .= "$nostr[0]<a href=\'$href\'$akstr[0]>�Ď׎����ʎގ������������</a>";
    &htmlout;
}

########################################
# Sub Trackback_ipban - ����IP����Υȥ�å��Хå���ػߡ������
########################################
sub trackback_ipban {
    
    my $rowid = $no;
    $no--;
    
    ####################
    # ping��õ��
    require MT::TBPing;
    my $tbping = MT::TBPing->load($page);    # �ȥ�å��Хå��ֹ��$page���Ϥ�
    if (!$tbping) {
        if ($hentities == 1) {
            $data = "trackback_ipban::MTPing ID '".encode_entities($page)."' �������Ǥ���";
        } else {
            $data = "trackback_ipban::MTPing ID '".$page."' �������Ǥ���";
        }
        &errorout;
        exit;      # exit����
    }
    
    require MT::IPBanList;
    my $ban = MT::IPBanList->new;
    $ban->blog_id($blog->id);
    $ban->ip($tbping->ip);
    $ban->save
        or die $ban->errstr;
    
    ####################
    # ����IP�����������줿�ȥ�å��Хå�������õ��
    my @tbpings = MT::TBPing->load(
            { blog_id => $cfg{Blog_ID}, ip => $tbping->ip});    
    
    for my $tbping (@tbpings) {
        
        #����tbping��°����Trackback��õ��
        require MT::Trackback;
        my $trackback = MT::Trackback->load($tbping->tb_id);
        if (!$trackback) {
            $data = "trackback_ipban::Trackback ID '".$tbping->tb_id."' �������Ǥ���";
            &errorout;
            exit;      # exit����
        }
        
        #����Trackback��°����Entry��õ��
        require MT::Entry;
        my $entry = MT::Entry->load($trackback->entry_id);
        if (!$entry) {
            $data = "trackback_ipban::Entry ID '".$trackback->entry_id."' �������Ǥ���";
            &errorout;
            exit;      # exit����
        }
        
        $data .= &conv_euc_z2h($tbping->excerpt)."<hr>";
        
        # �ȥ�å��Хå�ping���
        $tbping->remove()
            or die $tbping->errstr;

        ####################
        # MT3.0�ʾ�Ǥϡ���ӥ�ɤ�Хå����饦��ɤǹԤ�
        if ($mt->version_number() >= 3.0) {
            require MT::Util;
            MT::Util::start_background_task(sub {
                # entry�Υ�ӥ��
                $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                    or die $mt->errstr;
            });
        } else {
            # entry�Υ�ӥ��
            $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                or die $mt->errstr;
        }
    }
    
    $data = "IP��ػߎ؎��Ĥ��ɲä���".@tbpings."��ΎĎ׎����ʎގ����������ޤ�����<hr>";
    my $href = &make_href("trackback", $rowid, 0, $eid ,0);
    $data .= "$nostr[0]<a href=\'$href\'$akstr[0]>�Ď׎����ʎގ������������</a>";
    &htmlout;
    
    ####################
    # MT3.0�ʾ�Ǥϡ���ӥ�ɤ�Хå����饦��ɤǹԤ�
    if ($mt->version_number() >= 3.0) {
        require MT::Util;
        MT::Util::start_background_task(sub {
            # index�Υ�ӥ��
            $mt->rebuild_indexes( Blog => $blog )
                or die $mt->errstr;
        });
    } else {
        # index�Υ�ӥ��
        $mt->rebuild_indexes( Blog => $blog )
            or die $mt->errstr;
    }
}

########################################
# Sub Comment_ipban - ����IP����Υ����Ȥ�ػߡ������
########################################
sub comment_ipban {
    
    my $rowid = $no;
    $no--;
    
    ####################
    # comment��õ��
    require MT::Comment;
    my $comment = MT::Comment->load($page);    # �������ֹ��$page���Ϥ�
    if (!$comment) {
        if ($hentities == 1) {
            $data = "comment_ipban::Comment ID '".encode_entities($page)."' �������Ǥ���";
        } else {
            $data = "comment_ipban::Comment ID '".$page."' �������Ǥ���";
        }
        &errorout;
        exit;      # exit����
    }
    
    require MT::IPBanList;
    my $ban = MT::IPBanList->new;
    $ban->blog_id($blog->id);
    $ban->ip($comment->ip);
    $ban->save
        or die $ban->errstr;
    
    ####################
    # ����IP�����������줿�����Ȥ�����õ��
    my @comments = MT::Comment->load(
            { blog_id => $cfg{Blog_ID}, ip => $comment->ip});
    
    for my $comment (@comments) {
        
        require MT::Entry;
        my $entry = MT::Entry->load($comment->entry_id);
        if (!$entry) {
            $data = "comment_ipban::Entry ID '".$comment->entry_id."' �������Ǥ���";
            &errorout;
            exit;      # exit����
        }
        
        # �����Ⱥ��
        $comment->remove()
            or die $comment->errstr;
        
        ####################
        # MT3.0�ʾ�Ǥϡ���ӥ�ɤ�Хå����饦��ɤǹԤ�
        if ($mt->version_number() >= 3.0) {
            require MT::Util;
            MT::Util::start_background_task(sub {
                # entry�Υ�ӥ��
                $mt->rebuild_entry( Entry => $entry,, BuildDependencies => 1 )
                    or die $mt->errstr;
            });
        } else {
            # entry�Υ�ӥ��
            $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                or die $mt->errstr;
        }
    }
    
    $data = "IP��ػߎ؎��Ĥ��ɲä���".@comments."��Ύ��ҎݎĤ������ޤ�����<hr>";
    my $href = &make_href("comment", $rowid, 0, $eid, 0);
    $data .= "$nostr[0]<a href=\'$href\'$akstr[0]>���Ҏݎİ��������</a>";
    &htmlout;
    
    ####################
    # MT3.0�ʾ�Ǥϡ���ӥ�ɤ�Хå����饦��ɤǹԤ�
    if ($mt->version_number() >= 3.0) {
        require MT::Util;
        MT::Util::start_background_task(sub {
            # index�Υ�ӥ��
            $mt->rebuild_indexes( Blog => $blog )
                or die $mt->errstr;
        });
    } else {
        # index�Υ�ӥ��
        $mt->rebuild_indexes( Blog => $blog )
            or die $mt->errstr;
    }
}

########################################
# Sub Email_comments - �����ȤΥ᡼����������
########################################
sub email_comments {
    
    if ($email_new_comments){
        $blog->email_new_comments(0);
    }else{
        $blog->email_new_comments(1);
    }
    
    $blog->save
        or die $blog->errstr;
    
    if ($email_new_comments){
        $data = "���ҎݎĤΎҎ������Τ���ߤ��ޤ�����<hr>";
    }else{
        $data = "���ҎݎĤΎҎ������Τ�Ƴ����ޤ�����<hr>";
    }
    
    my $href = &make_href("", 0, $page, 0, 0);
    $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>���������</a>";
    &htmlout;

}

########################################
# Sub Confirm - �Ƽ��ǧ
########################################
sub confirm {
    
    my $rowid = $no;
    
    # ������ID��$page�Ǽ����Ϥ�
    if ($mode eq "confirm_comment_del"){
        
        require MT::Comment;
        my $comment = MT::Comment->load($page);    # �������ֹ��$page���Ϥ�
        if (!$comment) {
            if ($hentities == 1) {
                $data = "confirm_comment_del::Comment ID '".encode_entities($page)."' �������Ǥ���";
            } else {
                $data = "confirm_comment_del::Comment ID '".$page."' �������Ǥ���";
            }
            &errorout;
            exit;      # exit����
        }
        $data .="�����˰ʲ��Υ����Ȥ������Ƥ�����Ǥ�����<br>";
        
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"����󥻥뤹��\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"comment\">";
        $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
        $data .= "<input type=\"hidden\" name=\"page\" value=\"$page\">";
        $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"�������\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"comment_del\">";
        $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
        $data .= "<input type=\"hidden\" name=\"page\" value=\"$page\">";
        $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
        $data .= "<hr>";
        
        $data .= "Author:".&conv_euc_z2h($comment->author)."<br>";
        $data .= "Text:".&conv_euc_z2h($comment->text)."<br>";
        
    } elsif ($mode eq "confirm_entry_del"){

        require MT::Entry;
        my $entry = MT::Entry->load($eid);
        if (!$entry) {
            if ($hentities == 1) {
                $data = "confirm_entry_del::Entry ID '".encode_entities($eid)."' �������Ǥ���";
            } else {
                $data = "confirm_entry_del::Entry ID '".$eid."' �������Ǥ���";
            }
            &errorout;
            exit;      # exit����
        }
        
        require MT::Author;
        my $author = MT::Author->load({ id => $entry->author_id });    
        my $author_name = "";
        if ($author) {
            $author_name = &conv_euc_z2h($author->name);
        }
        
        $data .="�����˰ʲ���Entry�������Ƥ�����Ǥ�����<br>";
        
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"����󥻥뤹��\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"individual\">";
        $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
        $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"�������\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"entry_del\">";
        $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
        $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
        $data .= "<hr>";
        
        if ($author_name){
            $data .= "Author:".$author_name."<br>";
        }
        $data .= "Text:".&conv_euc_z2h($entry->text)."<br>";
        
    } elsif ($mode eq "confirm_trackback_del"){
        
        require MT::TBPing;
        my $tbping = MT::TBPing->load($page);    # �ȥ�å��Хå��ֹ��$page���Ϥ�
        if (!$tbping) {
            if ($hentities == 1) {
                $data = "confirm_trackback_del::MTPing ID '".encode_entities($page)."' �������Ǥ���";
            } else {
                $data = "confirm_trackback_del::MTPing ID '".$page."' �������Ǥ���";
            }
            &errorout;
            exit;      # exit����
        }
        
        $data .="�����˰ʲ���TB�������Ƥ�����Ǥ�����<br>";

        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"����󥻥뤹��\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"trackback\">";
        $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
        $data .= "<input type=\"hidden\" name=\"page\" value=\"$page\">";
        $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"�������\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"trackback_del\">";
        $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
        $data .= "<input type=\"hidden\" name=\"page\" value=\"$page\">";
        $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
        $data .= "<hr>";
        
        $data .= "BlogName:".&conv_euc_z2h($tbping->blog_name)."<br>";
        $data .= "Title:".&conv_euc_z2h($tbping->title)."<br>";
        $data .= "Excerpt:".&conv_euc_z2h($tbping->excerpt)."<br>";
        
    } else {
        $data .="confirm::mode '".$mode."' �������Ǥ���<br>";
    }
    
    &htmlout;
}

########################################
# Sub Admindoor - ��������URL��ɽ��
########################################
sub admindoor {
    my $href;
    if ($pw_text eq $cfg{AdminPassword}){
        $data .= '��������URL��';
        $href = &make_href("", 0, 0, 0, 0);
        $href .= '&key='.MT4i::Func::enc_crypt($cfg{AdminPassword}.$cfg{Blog_ID});
        $data .= "<a href=\"$href\">������</a>";
        $data .= '�Ǥ����؎ݎ����̎ގ����ώ��������塢®�䤫�ˡ�mt4i Manager�פˤ�"AdminDoor"���ͤ�"no"���ѹ����Ƥ���������<br>';
    }else{
        $data .= "�ʎߎ��܎��Ďޤ��㤤�ޤ�<hr>";
    }
    $key = "";
    $href = &make_href("", 0, 0, 0, 0);
    $data .= "$nostr[0]<a href='$href'$akstr[0]>���</a>";
    &htmlout;
}

########################################
# Sub Separate - ñ��������������ʸ��ʬ��
########################################

sub separate {
    my $text = $_[0];
    my $rowid = $_[1];
    
    # ���ڤ�ʸ���������˳�Ǽ���Ƥ���
    my @sprtstrlist = split(",",$cfg{SprtStr});
    
    # ��ʸ�ΥХ��ȿ�����Ƥ���
    my $maxlen = MT4i::Func::lenb_euc($text);
    
    # ����ʬ����֤��ᡢ$sprtbyte�س�Ǽ
    if (!$sprtbyte) {
        $sprtpage = 1;
        my $i = 0;
        $sprtbyte = "0";
        while ($i < $maxlen - $cfg{SprtLimit}) {
            my $tmpstart = $i;
            my $tmpend;
            
            if ($tmpstart + $cfg{SprtLimit} > $maxlen) {
                $tmpend = $maxlen - $tmpstart;
            } else {
                $tmpend = $cfg{SprtLimit};
            }
            
            # ���ڤ�ʸ����θ���
            my $sprtstart;
            my $tmptext = MT4i::Func::midb_euc($text, $tmpstart, $tmpend);
            foreach my $tmpsprtstr (@sprtstrlist) {
                if ($tmptext =~ /(.*)$tmpsprtstr/s) {
                    $tmptext = $1;
                    $sprtstart = MT4i::Func::lenb_euc($tmptext) + MT4i::Func::lenb_euc($tmpsprtstr);
                    last;
                }
            }
            if (!$sprtstart) {
                $sprtstart = $maxlen;
            }
            
            $sprtstart = $sprtstart + $tmpstart;
            
            # ʬ����֤�$sprtbyte�˳�Ǽ
            if ($sprtstart < $maxlen) {
                $sprtbyte .= ",$sprtstart";
            }
            $i = $sprtstart + 1;
        }
    }
    
    # $sprtbyte���ɤ߼��
    my @argsprtbyte = split(/,/, $sprtbyte);
    my $sprtstart = $argsprtbyte[$sprtpage - 1];
    my $sprtend;
    if ($sprtpage - 1 < $#argsprtbyte) {
        $sprtend = $argsprtbyte[$sprtpage] - $sprtstart;
    } else {
        $sprtend = $maxlen - $sprtstart;
    }
    
    ####################
    # ��ʸʸ��������
    
    my $tmptext = "";
    my $href = &make_href($mode, $rowid, 0, $eid, 0);
    
    # �ޤ��ϵ�����ʸ��ȴ��
    my $text = MT4i::Func::midb_euc($text, $sprtstart, $sprtend);
    
    ##### ­��ʤ���������äƤߤ� #####
    my $cnt_tag_o;
    my $cnt_tag_c;
    # UL����
    $cnt_tag_o = ($text =~ s!<ul!<ul!ig);
    $cnt_tag_c = ($text =~ s!</ul!</ul!ig);
    if ($cnt_tag_o < $cnt_tag_c) {
        for (my $i = 0; $i < $cnt_tag_c - $cnt_tag_o; $i++) {
            $text = '<ul>' . $text;
        }
    } elsif ($cnt_tag_o > $cnt_tag_c) {
        for (my $i = 0; $i < $cnt_tag_o - $cnt_tag_c; $i++) {
            $text .= '</ul>';
        }
    }
    # OL����
    $cnt_tag_o = ($text =~ s!<ol!<ol!ig);
    $cnt_tag_c = ($text =~ s!</ol!</ol!ig);
    if ($cnt_tag_o < $cnt_tag_c) {
        for (my $i = 0; $i < $cnt_tag_c - $cnt_tag_o; $i++) {
            $text = '<ol>' . $text;
        }
    } elsif ($cnt_tag_o > $cnt_tag_c) {
        for (my $i = 0; $i < $cnt_tag_o - $cnt_tag_c; $i++) {
            $text .= '</ol>';
        }
    }
    # BLOCKQUOTE����
    $cnt_tag_o = ($text =~ s!<blockquote!<blockquote!ig);
    $cnt_tag_c = ($text =~ s!</blockquote!</blockquote!ig);
    if ($cnt_tag_o < $cnt_tag_c) {
        for (my $i = 0; $i < $cnt_tag_c - $cnt_tag_o; $i++) {
            $text = '<blockquote>' . $text;
        }
    } elsif ($cnt_tag_o > $cnt_tag_c) {
        for (my $i = 0; $i < $cnt_tag_o - $cnt_tag_c; $i++) {
            $text .= '</blockquote>';
        }
    }
    # FONT����
    $cnt_tag_o = ($text =~ s!<font!<font!ig);
    $cnt_tag_c = ($text =~ s!</font!</font!ig);
    if ($cnt_tag_o < $cnt_tag_c) {
        for (my $i = 0; $i < $cnt_tag_c - $cnt_tag_o; $i++) {
            $text = '<font>' . $text;
        }
    } elsif ($cnt_tag_o > $cnt_tag_c) {
        for (my $i = 0; $i < $cnt_tag_o - $cnt_tag_c; $i++) {
            $text .= '</font>';
        }
    }
    
    # �ڡ�����󥯡ʾ��
    $tmptext .= "&lt; �͎ߎ����ް�ư:";
    for (my $i = 1; $i <= $#argsprtbyte + 1; $i++)  {
        if ($i == $sprtpage) {
            $tmptext .= " $i";
        } else {
            $tmptext .= " <a href=\"$href&amp;sprtpage=$i&amp;sprtbyte=$sprtbyte\">$i</a>";
        }
    }
    $tmptext .= " &gt;<br>";
    
    # ������ʸ
    $tmptext .= $text;
    
    # �ڡ�����󥯡ʲ���
    $tmptext .= "<br>&lt; �͎ߎ����ް�ư:";
    for (my $i = 1; $i <= $#argsprtbyte + 1; $i++)  {
        if ($i == $sprtpage) {
            $tmptext .= " $i";
        } else {
            $tmptext .= " <a href=\"$href&amp;sprtpage=$i&amp;sprtbyte=$sprtbyte\">$i</a>";
        }
    }
    $tmptext .= " &gt;";
    
    return $tmptext;
}

########################################
# Sub Conv_euc_z2h - ��EUC-JP�����Ѣ�Ⱦ���Ѵ�
########################################

sub conv_euc_z2h {
    my $tmpstr = $_[0];

    return $tmpstr unless $tmpstr;

    # ��������EUC-JP���Ѵ�
    if ($conv_in ne "euc") {
        if ($conv_in eq "utf8" && $ecd == 1) {
            $tmpstr = encode("cp932",decode("utf8",$tmpstr));
            $tmpstr = encode("euc-jp",decode("shiftjis",$tmpstr));
        } else {
            $tmpstr = Jcode->new($tmpstr, $conv_in)->euc;
        }
    }
    
    # ɽ��ʸ���������ʸ����Ⱦ�Ѥ��Ѵ�
    if ($cfg{Z2H} eq "yes") {
        if ($ecd == 1) {
            Encode::JP::H2Z::z2h(\$tmpstr);
            $tmpstr = Jcode->new($tmpstr,'euc')->tr('��-�ڣ�-����-���������ʡˡ��', 'A-Za-z0-9/!?()=&');
        } else {
            $tmpstr = Jcode->new($tmpstr,'euc')->z2h->tr('��-�ڣ�-����-���������ʡˡ��', 'A-Za-z0-9/!?()=&');
        }
    }
    return $tmpstr;
}

########################################
# Sub Img_Url_Conv - ����URL�Υ���å����%2F���Ѵ�
########################################

sub img_url_conv {
    my $tmpstr = $_[0];
    my $str = "";
    
    # �롼�פ��ʤ���<img>������URL���ִ�
    while ($tmpstr =~ /(<img(?:[^"'>]|"[^"]*"|'[^']*')*src=)("[^"]*"|'[^']*')((?:[^"'>]|"[^"]*"|'[^']*')*>)/i) {
        my $front = $` . $1;
        my $url = $2;
        my $end = $3 . $';
        
        # ���֥롦���󥰥륯�����ơ������������
        $url =~ s/["']//g;
        
        # "/"��"%2F"
        $url =~ s/\//\%2F/g;
        
        # ���֥륯�����ơ��������䤤�Ĥķ��
        $str .= "$front\"" . $url;
        $tmpstr = "\"$end";
    }
    $str .= $tmpstr;
    return $str;
}

########################################
# Sub Conv_Redirect - ��󥯤�URL�������쥯����ͳ���Ѵ�
########################################

sub conv_redirect {
    my $tmpstr = $_[0];
    my $ref_rowid = $_[1];
    my $ref_eid = $_[2];
    my $str = "";
    
    # �롼�פ��ʤ���URL���ִ�
    while ($tmpstr =~ /(<a(?:[^"'>]|"[^"]*"|'[^']*')*href=)("[^"]*"|'[^']*')((?:[^"'>]|"[^"]*"|'[^']*')*>)/i) {
        my $front = $` . $1;
        my $url = $2;
        my $end = $3;
        my $backward = $';
        my $tmpfront = $1;
        my $tmpend = $3;
        my $lnkstr = "";

        my $title;
        
        # title°������Ф�
        if ($tmpfront =~ /title=/i) {
            my $tmpstr = $tmpfront;
            $tmpstr =~ s/.*<a(?:[^"'>]|"[^"]*"|'[^']*')*title=("[^"]*"|'[^']*')(?:[^"'>]|"[^"]*"|'[^']*')*\Z/$1/i;
            $title = $tmpstr;
        } elsif ($tmpend =~ /title=/i) {
            my $tmpstr = $tmpend;
            $tmpstr =~ s/\A.*(?:[^"'>]|"[^"]*"|'[^']*')*title=("[^"]*"|'[^']*')(?:[^"'>]|"[^"]*"|'[^']*')*>/$1/i;
            $title = $tmpstr;
        }
        # ���֥롦���󥰥륯�����ơ������������
        $title =~ s/["']//g;
        $url =~ s/["']//g;
        
        if ($title !~ /$cfg{ExitChtmlTrans}/) {
            my $tmpurl = &make_href("redirect", $ref_rowid, 0, 0, $ref_eid);
            
            # "/"��"%2F"
            $url =~ s!/!\%2F!g;
            
            # "&"��"%26"
            $url =~ s/\&/\%26/g;
            
            $url = $tmpurl . '&amp;url=' . $url;
        } else {
            # �����б��ޡ���
            $lnkstr = $ExitChtmlTransStr;
        }
        # ���֥륯�����ơ��������䤤�Ĥķ��
        $str .= "$front\"" . $url;
        $tmpstr = "\"$end" . $lnkstr . $backward;
        
    }
    $str .= $tmpstr;

    # title��target°���κ���ʥХ��ȿ���̵�̡�
    $str =~ s/ target=["'][^"']*["']//ig;
    $str =~ s/ title=["'][^"']*["']//ig;
    
    return $str;
}

########################################
# Sub Redirector - ������쥯��
########################################

sub redirector {
    # URL���Ѵ�
    my ($lnkstr,$lnkurl) = &chtmltrans($redirect_url);
    
    # ��Х����Ѥ�URL�����Ĥ��ä���Ƚ��
    if ($lnkstr) {
        # ��Х�����URL�����Ĥ��ä����
        $data .= '<p>�̤Ύ����Ĥ؎��ގ��ݎ̎ߤ��褦�Ȥ��Ƥ��ޤ���';
        $data .= '�������á��ӎʎގ��ٵ����Ѥ�URL�����Ĥ���ޤ�����</p>';
        $data .= "<p>�����؎���<br>$lnkstr<a href=\"$lnkurl\">$lnkurl</a></p>";
        $data .= '<p>����������URL�ˤʤ�ޤ���';
        $data .= '�嵭�Ǿ�꤯ɽ���Ǥ��ʤ���硢����URL�򤪻��������</p>';
        $data .= "<p>�����؎���<br><a href=\"$redirect_url\">$redirect_url</a></p>";
    } else {
        # ��Х�����URL�����Ĥ���ʤ��ä����
        $data .= '<p>�̤Ύ����Ĥ؎��ގ��ݎ̎ߤ��褦�Ȥ��Ƥ��ޤ���</p>';
        $data .= "<p>�����؎���<br><a href=\"$redirect_url\">$redirect_url</a></p>";
        $data .= '<p>�嵭URL�Ύ����ĤϷ������ä�������ɽ���Ǥ��ʤ����⤷��ޤ��󤬡�';
        $data .= '����URL�Ǥ����ɽ���Ǥ��뤫�⤷��ޤ���</p>';
        $data .= "<p>�����؎���<br><a href=\"$lnkurl\">$lnkurl</a></p>";
    }
    $data .= "<hr>";
    my $href = &make_href("individual", $no, 0, $ref_eid, 0);
    $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>���</a>";
    $data .= "<hr>";
    &htmlout;
}

########################################
# Sub Chtmltrans - ��󥯤�URL��chtmltrans��ͳ����¾���Ѵ�
# ���͡�Perl��⢪http://www.din.or.jp/~ohzaki/perl.htm#HTML_Tag
########################################

sub chtmltrans {
    my $url = $_[0];
    my $lnkstr = "";
    
    if ($url =~ m/.*http:\/\/www.amazon.co.jp\/exec\/obidos\/ASIN\/.*/g) {
        # Amazon���̾��ʥ�󥯤ʤ�i-mode�б����Ѵ�
        $url =~ s!exec/obidos/ASIN/!gp/aw/rd.html\?a=!g;
        $url =~ s!ref=nosim/!!g;
        $url =~ s!ref=nosim!!g;
        $url =~ s!/$!!g;
        $url =~ s!/([^/]*-22)!&amp;uid=NULLGWDOCOMO&amp;url=/gp/aw/d.html&amp;lc=msn&amp;at=$1!;
        $url .= '&amp;dl=1';
        $lnkstr = $mt4ilinkstr;
    } elsif ($url =~ m!.*http://www.amazon.co.jp/gp/product/.*!g) {
        # �� Amazon ��󥯤ʤ�����б� URL ���Ѵ�
        # ���̾��ʥ�󥯤Υƥ����ȤΤ�
        $url =~ s!(http://www.amazon.co.jp/gp/)product/(.*)\?ie=(.*)&tag=(.*)&linkCode.*!$1aw/rd.html?ie=$3&dl=1&uid=NULLGWDOCOMO&a=$2&at=$4&url=%2Fgp%2Faw%2Fd\.html!g;
    } elsif ($url =~ m/.*http:\/\/www.amazon.co.jp\/gp\/redirect.html.*/g) {
        # �� Amazon ��󥯤ʤ�����б� URL ���Ѵ�
        # �ƥ����ȥ�� | ����Υڡ���
        $url =~ s!(http://www.amazon.co.jp/gp/).*product/(.*)\?ie=(.*)&tag=(.*)&linkCode.*!$1aw/rd.html?ie=$3&dl=1&uid=NULLGWDOCOMO&a=$2&at=$4&url=%2Fgp%2Faw%2Fd\.html!g;
    } elsif ($url =~ m/.*http:\/\/www.amazlet.com\/browse\/ASIN\/.*/g) {
        # Amazlet�ؤΥ�󥯤ʤ顢Amazon��i-mode�б����Ѵ�
        $url =~ s!www.amazlet.com/browse/ASIN/!www.amazon.co.jp/gp/aw/rd.html?a=!g;
        $url =~ s!/ref=nosim/!!g;
        $url =~ s!/$!!g;
        $url =~ s!/([^/]*-22)!&amp;uid=NULLGWDOCOMO&amp;url=/gp/aw/d.html&amp;lc=msn&amp;at=$1!;
        $url .= '&amp;dl=1';
        $lnkstr = $mt4ilinkstr;
    } else {
        # ���������
        my $mt4ilink = MT4i::Func::get_mt4ilink($url);
        
        if ($mt4ilink) {
            $url = $mt4ilink;
            $lnkstr = $mt4ilinkstr;
        } else {
            if ($cfg{MobileGW} eq '1') {              # �̶Х֥饦��
                # 'http://'����
                $url =~ s!http://!!g;
                # URL������
                my $chtmltransurl = 'http://www.sjk.co.jp/c/w.exe?y=';
                $url = $chtmltransurl . $url;
            } elsif ($cfg{MobileGW} eq '2') {           # Google mobile Gateway
                # "/"��"%2F"��"?"��"%3F"��"+"��"%2B"
                $url =~ s/\//\%2F/g;
                $url =~ s/\?/\%3F/g;
                $url =~ s/\+/\%2B/g;
                # URL������
                my $chtmltransurl = 'http://www.google.co.jp/gwt/n?u=';
                $url = $chtmltransurl . $url;
            }
        }
    }
    return ($lnkstr,$url);
}

########################################
# Sub Htmlout - HTML�ν���
########################################

sub htmlout {
    # blog_name������Ԥ���
    my $hd_blog_name = $blog_name;
    $hd_blog_name =~ s!<br>!!ig; 
    $hd_blog_name =~ s!<br />!!ig; 
    
    # HTML�إå�/�եå����
    $data = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD Compact HTML 1.0 Draft//EN\"><html><head><meta name=\"CHTML\" HTTP-EQUIV=\"content-type\" CONTENT=\"text/html; charset=Shift_JIS\"><meta http-equiv=\"Pragma\" content=\"no-cache\"><meta http-equiv=\"Cache-Control\" content=\"no-cache\"><meta http-equiv=\"Cache-Control\" content=\"max-age=0\"><title>$hd_blog_name mobile ver.</title></head><body bgcolor=\"$cfg{BgColor}\" text=\"$cfg{TxtColor}\" link=\"$cfg{LnkColor}\" alink=\"$cfg{AlnkColor}\" vlink=\"$cfg{VlnkColor}\">" . $data;
    if (exists $cfg{AdmNM}) {
        $data .= "<p><center>������:";
        if (exists $cfg{AdmML}) {
            $cfg{AdmML} =~ s/\@/\&#64;/g;
            $cfg{AdmML} =~ s/\./\&#46;/g;
            $data .= "<a href=\"mailto:$cfg{AdmML}\">$cfg{AdmNM}</a>";
        } else {
            $data .= "$cfg{AdmNM}";
        }
        $data .= "</center></p>";
    }
    $data .= "<p><center>Powered by<br>";
    # �����ԥ⡼�ɤǤ�MT4i�����ڡ����ؤΥ��󥫡���ɽ�����ʤ�
    if ($admin_mode eq 'yes') {
        $data .= "MT4i v$version";
    } else {
        $data .= "<a href=\"http://hazama.nu/pukiwiki/?MT4i\">MT4i v$version</a>";
    }
    $data .= "</center></p></body></html>";
    
    # ɽ��ʸ�����Shift_JIS���Ѵ�
    if ($ecd == 1) {
        $data = encode("shiftjis",decode("euc-jp",$data));
    } else {
        $data = Jcode->new($data, 'euc')->sjis;
    }
    
    # ɽ��
    binmode(STDOUT);
    print "Content-type: text/html; charset=Shift_JIS\n";
    print "Content-Length: ",length($data),"\n\n";
    print $data;
}

########################################
# Sub Errorout - ���顼�ν���
########################################

sub errorout {
    # HTML�إå�/�եå����
    $data = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD Compact HTML 1.0 Draft//EN\"><html><head><meta name=\"CHTML\" HTTP-EQUIV=\"content-type\" CONTENT=\"text/html; charset=Shift_JIS\"><title>Error</title></head><body>" . $data . "</body></html>";
    
    # ɽ��ʸ�����Shift_JIS���Ѵ�
    if ($ecd == 1) {
        $data = encode("shiftjis",decode("euc-jp",$data));
    } else {
        $data = Jcode->new($data, 'euc')->sjis;
    }
    
    # ɽ��
    binmode(STDOUT);
    print "Content-type: text/html; charset=Shift_JIS\n";
    print "Content-Length: ",length($data),"\n\n";
    print $data;
}

##############################################################
# Sub conv_datetime - YYYYMMDDhhmmss�� MM/DD hh:mm ���Ѵ�
##############################################################

sub conv_datetime {
    if ($mode || (!$mode && $cfg{DT} eq "dt")) {
        $_[0] =~ s/\d\d\d\d(\d\d)(\d\d)(\d\d)(\d\d)\d\d/($1\/$2 $3:$4)/;
    } elsif (!$mode && $cfg{DT} eq "d") {
        $_[0] =~ s/\d\d\d\d(\d\d)(\d\d)\d\d\d\d\d\d/($1\/$2)/;
    } else {
        $_[0] = "";
    }
    return $_[0];
}

############################################################
# Sub Check_Category - ����ȥ�Υץ饤�ޥꥫ�ƥ����٥�����
#  �ץ饤�ޥꥫ�ƥ��꤬��ɽ�����ꤵ��Ƥ�����Ϻǽ�˽ФƤ���
#  ���֥��ƥ���Υ�٥�����
############################################################
sub check_category{
    my ($entry) = @_;
    my $cat_label;
    require MT::Category;
    require MT::Placement;
    my @categories = MT::Category->load({ blog_id => $cfg{Blog_ID} }, { unique => 1 });
    if (@categories) {
        my $place = MT::Placement->load({ entry_id => $entry->id, is_primary => 1 });
        if ($place) {
            my $match_cat = 0;
            if ($mode ne 'entryform' || $admin_mode eq 'no') {
                my @nondispcats = split(",", $cfg{NonDispCat});
                for my $nondispcat (@nondispcats) {
                    if ($place->category_id == $nondispcat) {
                        $match_cat = 1;
                        last;
                    }
                }
            }
            if ($match_cat == 0) {
                for my $category (@categories) {
                    if ($category->id == $place->category_id) {
                        if ($cfg{CatDescReplace} eq "yes") {
                            $cat_label = &conv_euc_z2h($category->description);
                        } else {
                            $cat_label = &conv_euc_z2h($category->label);
                        }
                        last;
                    }
                }
            } else {
                my @places = MT::Placement->load({ entry_id => $entry->id });
                my @nondispcats = split(",", $cfg{NonDispCat});
                for my $category (@categories) {
                    my $match_cat = 0;
                    for my $nondispcat (@nondispcats) {
                        if ($category->id == $nondispcat) {
                            $match_cat = 1;
                            last;
                        }
                    }
                    if ($match_cat == 0) {
                        for my $place (@places) {
                            if ($category->id == $place->category_id) {
                                if ($cfg{CatDescReplace} eq "yes") {
                                    $cat_label = &conv_euc_z2h($category->description);
                                } else {
                                    $cat_label = &conv_euc_z2h($category->label);
                                }
                                $match_cat = 1;
                                last;
                            }
                        }
                        if ($match_cat == 1) {
                            last;
                        }
                    }
                }
            }
        }
    }
    return $cat_label;
}

########################################
# Sub Conv_Euc2icode - EUC-JP��MT���ѥ������Ѵ�
########################################

sub conv_euc2icode {
    my ($str) = @_;
    if ($conv_in ne 'euc') {
        if ($conv_in eq 'utf8' && $ecd == 1) {
            $str = encode("shiftjis",decode("euc-jp",$str));
            $str = encode("utf8",decode("cp932",$str));
        } else {
            $str = Jcode->new($str, 'euc')->$conv_in();
        }
    }
    return $str;
}

##################################################
# Sub Get_CatList - ���쥯���ѥ��ƥ���ꥹ�Ȥμ���
##################################################
sub get_catlist {
    my @categories;

    require MT::Category;
    my @cats = MT::Category->top_level_categories($cfg{Blog_ID});

    # ������
    my @s_cats = &sort_cat(@cats);

    # ���֥��ƥ���μ���
    foreach my $category (@s_cats) {
        my @c_cats = &get_subcatlist($category, 0);
        foreach my $c_category (@c_cats) {
            push @categories, $c_category;
        }
    }
    return @categories;
}

##################################################
# Sub Get_SubCatList - ���쥯���ѥ��֥��ƥ���ꥹ�Ȥμ���
##################################################
sub get_subcatlist {
    my $category = shift;
    my $hierarchy = shift;
    
    # �����ԥ⡼�ɤǤʤ����ˤ���ɽ�����ƥ�����������
    # �ƥ��ƥ��꤬��ɽ���ʤ�ҥ��ƥ����ɽ�����ʤ�
    if ($admin_mode ne "yes"){
        my @nondispcats = split(",", $cfg{NonDispCat});
        my $match_cat = 0;
        for my $nondispcat (@nondispcats) {
            if ($category->id == $nondispcat) {
                $match_cat = 1;
                last;
            }
        }
        if ($match_cat > 0) {
            return;
        }
    }
    
    ####################
    # ���ƥ�������
    my %terms = (blog_id => $cfg{Blog_ID});
    # �����ԥ⡼�ɤǤʤ���Х��ơ�������'����'�Υ���ȥ�Τߥ������
    if ($admin_mode ne "yes"){
        $terms{'status'} = 2;
    }
    require MT::Entry;
    require MT::Placement;
    my $count = MT::Entry->count( \%terms,
                                { join => [ 'MT::Placement', 'entry_id',
                                { blog_id => $cfg{Blog_ID}, category_id => $category->id } ] });
    #if ($count == 0) {
    #    return;
    #}

    my @categories;

    my $blank;
    foreach (my $i = 0; $i < $hierarchy; $i++) {
        $blank .= "-";
    }
    
    my $id = $category->{column_values}->{id};
    my $label;
    if ($cfg{CatDescReplace} eq "yes"){
        $label = &conv_euc_z2h($category->{column_values}->{description});
        # ���ƥ���̾�֤ä��ڤ�
        if ($cfg{LenCutCat} > 0) {
            if (MT4i::Func::lenb_euc($label) > $cfg{LenCutCat}) {
                $label = MT4i::Func::midb_euc($label, 0, $cfg{LenCutCat});
            }
        }
        $label = $blank . $label;
    } else {
        $label = &conv_euc_z2h($category->{column_values}->{label});
        # ���ƥ���̾�֤ä��ڤ�
        if ($cfg{LenCutCat} > 0) {
            if (MT4i::Func::lenb_euc($label) > $cfg{LenCutCat}) {
                $label = MT4i::Func::midb_euc($label, 0, $cfg{LenCutCat});
            }
        }
        $label = $blank . $label;
    }

    if ($cat == $id){
        push @categories, "<option value=\"$id\" selected>$label($count)";
    } else {
        push @categories, "<option value=\"$id\">$label($count)";
    }

    require MT::Category;
    my @cats = $category->children_categories;
    if (@cats) {
        # ������
        my @s_cats = &sort_cat(@cats);

        # ���֥��ƥ���μ���
        foreach my $s_cat (@s_cats) {
            my @c_cats = &get_subcatlist($s_cat, $hierarchy + 1);
            foreach my $c_cat (@c_cats) {
                push @categories, $c_cat;
            }
        }
    }
    return @categories;
}

##################################################
# Sub Sort_Cat - ���쥯���ѥ��ƥ���ꥹ�ȤΥ�����
##################################################
sub sort_cat {
    my @cats = @_;
    
    if ($cfg{CatDescSort} eq "asc"){
        @cats = sort { $a->{column_values}->{label} cmp $b->{column_values}->{label} } @cats;
    }elsif ($cfg{CatDescSort} eq "desc"){
        @cats = reverse sort { $a->{column_values}->{label} cmp $b->{column_values}->{label} } @cats;
    }
    return @cats;
}

##################################################
# Sub Get_NonDispCats - ��ɽ�����ƥ���ꥹ�Ȥμ���
##################################################
sub get_nondispcats {
    my @nondispcats = split(",", $cfg{NonDispCat});
    my @nonsubdispcats;
    foreach my $nondispcatid (@nondispcats) {
        # ID���饫�ƥ��ꥪ�֥������Ȥ����
        require MT::Category;
        my $category = MT::Category->load($nondispcatid);
        if (defined $category) {
            my @sub_categories = MT4i::Func::get_subcatobjlist($category);
            foreach my $sub_category (@sub_categories) {
                push @nonsubdispcats, $sub_category->id;
            }
        }
    }
    push @nondispcats, @nonsubdispcats;
    
    return @nondispcats;
}
