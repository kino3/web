#!/usr/bin/perl
##################################################
#
# MovableType用 i-mode変換スクリプト
# 「MT4i」
my $version = "2.25";
# Copyright (C) 太鉄 All rights reserved.
# Special Thanks
#           ヴァリウム男爵 & Tonkey & drry
#
# MT4i - t2o2-Wiki
#  →http://www.hazama.nu/pukiwiki/index.php?MT4i
# TonkeyさんのTonkey Magic
#  →http://tonkey.mails.ne.jp/
# ヴァリウム男爵の人生迷い箸
#  →http://mayoi.net/
# drryさんのdrry+@->Weblog
#  →http://blog.drry.jp/
#
# -- 言い訳ここから --
# ぶっちゃけ、行き当たりばったりの「動けばいいや」で
# コーディングしてますし、Perlに関しては素人同然なので、
# ソースが汚い＆技術的に未熟な点はご容赦ください。
# -- 言い訳ここまで --
#
##################################################

use strict;
use CGI;

# 外部ファイルの読み込み
eval {require 'mt4ilib/Config.pl'; 1} || die print "Content-type: text/plain; charset=EUC-JP\n\n\"./mt4ilib/Config.pl\"が見付かりません。";
eval {require 'mt4ilib/Func.pl'; 1} || die print "Content-type: text/plain; charset=EUC-JP\n\n\"./mt4ilib/Func.pl\"が見付かりません。";

# 設定読み込み
my %cfg = Config::Read("./mt4icfg.cgi");

unshift @INC, $cfg{MT_DIR} . 'lib';
unshift @INC, $cfg{MT_DIR} . 'extlib';

####################
# HTML::Entities の有無調査
my $hentities;
eval 'use HTML::Entities;';
if($@){
    $hentities = 0;
}else{
    $hentities = 1;
}

####################
# Jcode.pmの有無調査
eval 'use Jcode;';
if($@){
    print "Content-type: text/plain; charset=EUC-JP\n\n\"Jcode.pm\"がインストールされていません。";
    exit;
}

####################
# User Agent によるキャリア判別
# 参考：http://specters.net/cgipon/labo/c_dist.html
my $ua;
my @user_agent = split(/\//,$ENV{'HTTP_USER_AGENT'});
my $png_flag;
if ($user_agent[0] eq 'ASTEL') {
    # ドットi 用の処理
    $ua = 'other';
} elsif ($user_agent[0] eq 'UP.Browser') {
    # EZweb 旧端末用の処理
    $ua = 'ezweb';
} elsif ($user_agent[0] =~ /^KDDI/) {
    # EZweb WAP2.0 対応端末用の処理
    $ua = 'ezweb';
} elsif ($user_agent[0] eq 'PDXGW') {
    # H" 用の処理
    $ua = 'other';
} elsif ($user_agent[0] eq 'DoCoMo') {
    # i-mode 用の処理
    $ua = 'i-mode';
} elsif ($user_agent[0] eq 'Vodafone' ||
         $user_agent[0] eq 'SoftBank') {
    # J-SKY 用の処理
    $ua = 'j-sky';
} elsif ($user_agent[0] eq 'J-PHONE') {
    # J-SKY 用の処理
    $ua = 'j-sky';
    
    # PNGしか表示できない機種はこれだけなので事前にチェックする
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
    # AirH"PHONE用の処理
    $ua = 'i-mode';
} elsif ($user_agent[0] eq 'L-mode') {
    # L-mode 用の処理
    $ua = 'other';
} else {
    # それ以外
    $ua = 'other';
}

####################
# AccessKey用文字列生成
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
    # i-mode 及び EZweb
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
# 引数の取得
my $q = new CGI();

if (!$cfg{Blog_ID}) {
    $cfg{Blog_ID} = $q->param("id");    # blog ID
}
my $mode = $q->param("mode");            # 処理モード
my $no = $q->param("no");                # エントリーNO
my $eid = $q->param("eid");                # エントリーID
my $ref_eid = $q->param("ref_eid");        # 元記事のエントリーID
my $page = $q->param("page");            # ページNO
my $sprtpage = $q->param("sprtpage");    # 分割ページ数
my $sprtbyte = $q->param("sprtbyte");    # ページ分割byte数
my $redirect_url = $q->param("url");    # リダイレクト先のURL
my $img = $q->param("img");                # 画像のURL
my $cat = $q->param("cat");                # カテゴリID
my $post_from = $q->param("from");        # 投稿者
my $post_mail = $q->param("mail");        # メール
my $post_text = $q->param("text");        # コメント

my $pw_text = $q->param("pw_text");        # 暗号化パスワード
my $key = $q->param("key");                # 暗号化キー
my $entry_cat = $q->param("entry_cat");                    # エントリーのカテゴリー
my $entry_title = $q->param("entry_title");                # エントリーのタイトル
my $entry_text = $q->param("entry_text");                # エントリーの内容
my $entry_text_more = $q->param("entry_text_more");        # エントリーの追記
my $entry_excerpt = $q->param("entry_excerpt");            # エントリーの概要
my $entry_keywords = $q->param("entry_keywords");        # エントリーのキーワード
my $entry_tags = $q->param("entry_tags");                # エントリーのタグ
my $post_status = $q->param("post_status");                # エントリーのステータス
my $post_status_old = $q->param("post_status_old");        # エントリーの編集前のステータス
my $allow_comments = $q->param("allow_comments");        # エントリーのコメント許可チェック
my $allow_pings = $q->param("allow_pings");                # エントリーのping許可チェック
my $text_format = $q->param("convert_breaks");            # エントリーのテキストフォーマット
my $entry_created_on = $q->param("entry_created_on");    # エントリーの作成日時
my $entry_authored_on = $q->param("entry_authored_on");    # エントリーの公開日時

# PerlMagick の有無調査
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

my $data;    # 表示文字列用の変数を宣言する

#管理者用暗号化キーをチェック
my $admin_mode;
if (($key ne "")&&(MT4i::Func::check_crypt($cfg{AdminPassword}.$cfg{Blog_ID},$key))){
    $admin_mode = 'yes';
}else{
    $admin_mode = 'no';
    $key = "";
}

####################
# mt.cfgの読み込み
eval{ require MT; };
if($@){
    $data .= "<p>MT.pmが見付かりません。<br>";
    $data .= "MTホームディレクトリの設定を見直してください。</p>";
    $data .= $@;
    &errorout;
    exit;      # exitする
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
# Encode.pmの有無調査
my $ecd;
eval 'use Encode;';
if($@){
    $ecd = 0;
}else{
    eval 'use Encode::JP::H2Z;';
    $ecd = 1;
}

####################
# blog IDが指定されていなかった場合はエラー
if (!$cfg{Blog_ID}) {
    $data = "Error：引数にblog IDを指定してください。<br>";
    # blog一覧表示
    $data .= "<br>";
    require MT::Blog;
    my @blogs = MT::Blog->load(undef,
                            {unique => 1});

    # ソート
    @blogs = sort {$a->id <=> $b->id} @blogs;
    
    $data .= '<table border="1">';
    $data .= '<tr><th style="color:#FF0000;">blog ID</th><th>blog Name</th><th>Description</th></tr>';
    
    # 表示
    for my $blog (@blogs) {
        my $blog_id = $blog->id;
        my $blog_name = &conv_euc_z2h($blog->name);
        my $blog_description = &conv_euc_z2h($blog->description);
        $data .= "<tr><th style=\"color:#FF0000;\">$blog_id</th><td><a href=\"./$cfg{MyName}?id=$blog_id\">$blog_name</a></td><td>$blog_description</td></tr>";
    }

    $data .= '</table><br><span style="font-weight:bold;">blog ID の指定方法：</span><br>　MT4i.cgi の設定にて "<span style="font-weight:bold;">$blog_id</span>" に上記 <span style="color:#FF0000;font-weight:bold;">blog ID</span> を指定するか、<br>　もしくは上記 <span style="color:#FF0000;font-weight:bold;">blog Name</span> にﾘﾝｸされている URL でｱｸｾｽする。';
    
    &errorout;
    exit;      # exitする
}

####################
# PublishCharsetの取得
my $conv_in = lc $mt->{cfg}->PublishCharset eq lc "Shift_JIS"   ? "sjis"
            : lc $mt->{cfg}->PublishCharset eq lc "ISO-2022-JP" ? "jis"
            : lc $mt->{cfg}->PublishCharset eq lc "UTF-8"       ? "utf8"
            : lc $mt->{cfg}->PublishCharset eq lc "EUC-JP"      ? "euc"
            : "utf8";

####################
# blog名及び概要の取得
require MT::Blog;
my $blog = MT::Blog->load($cfg{Blog_ID},
                      {unique => 1});

# 不正なblog ID
if (!$blog) {
    if ($hentities == 1) {
        $data = 'ID \''.encode_entities($cfg{Blog_ID}).'\' のblogは存在しません。';
    } else {
        $data = 'ID \''.$cfg{Blog_ID}.'\' のblogは存在しません。';
    }
    &errorout;
    exit;      # exitする
}

# blog名、概要、コメント関連設定を変数に格納
my $blog_name = &conv_euc_z2h($blog->name);
my $description = &conv_euc_z2h($blog->description);
my $sort_order_comments = $blog->sort_order_comments;
my $email_new_comments = $blog->email_new_comments;
my $email_new_pings = $blog->email_new_pings;
my $convert_paras = $blog->convert_paras;
my $convert_paras_comments = $blog->convert_paras_comments;

####################
# 引数$modeの判断
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


# 管理者用バックドアの表示
if ($cfg{AdminDoor} eq "yes"){
    if ($mode eq 'admindoor')    { &admindoor }
}

#--- ここから先は管理モードでしか実行できない ---

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
# Sub Main - トップページの描画
########################################

sub main {
    if(!$mode && !$page) { $page = 0 }
    if ($cfg{AccessKey} eq "yes" && ($ua eq "i-mode" || $ua eq "j-sky" || $ua eq "ezweb")) {
        # 携帯電話からのアクセスかつアクセスキー有効の場合は$cfg{DispNum}を6以下にする
        if ($cfg{DispNum} > 6) {
            $cfg{DispNum} = 6;
        }
    }
    my $rowid;
    if($page == 0) { $rowid = 0 } else { $rowid = $page * $cfg{DispNum} }
    
    ####################
    # 総件数の取得
    my $ttlcnt = &get_ttlcnt;
    
    ####################
    # 一覧の取得
    my @entries = &get_entries($rowid, $cfg{DispNum});
    
    # 一覧件数取得（$cfg{DispNum}より少ない可能性がある為）
    my $rowcnt = @entries + 1;
    
    ####################
    # 表示文字列生成
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
    
    # 管理者モード
    if ($admin_mode eq 'yes'){
        $data .= "<h2 align=\"center\"><font color=\"$cfg{TitleColor}\">管理者モード</font></h2>";
    }
    
    if ($cfg{Dscrptn} eq "yes" && $page == 0 && $description) {
        my $tmp_data .= "<hr><center>$description</center>";
        #単なる改行を<br>タグに置換
        #(「ウェブログの説明」に改行が混ざるとauで表示されない不具合への対処)
        $tmp_data=~s/\r\n/<br>/g;
        $tmp_data=~s/\r/<br>/g;
        $tmp_data=~s/\n/<br>/g;
        $data .= $tmp_data;
    }
    $data .= "<hr>";
    
    # カテゴリセレクタ
    if ($cfg{CatSelect} == 1) {
        $data .= "<center><form action=\"$cfg{MyName}\">";
        if ($key){
            $data .= "<input type=hidden name=\"key\" value=\"$key\">";
        }
        $data .= "<select name=\"cat\">";
        $data .= "<option value=0>すべて";
    
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
                # 管理者モードでない場合には非表示カテゴリを処理する
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
                
                # カテゴリ名の日本語化を$MTCategoryDescriptionで表示している場合に
                # カテゴリセレクタの内容を置換する
                if ($cfg{CatDescReplace} eq "yes"){
                    $label = &conv_euc_z2h($category->description);
                }else{
                    $label = &conv_euc_z2h($category->label);
                }
                my $cat_id = $category->id;
                require MT::Entry;
                require MT::Placement;
                ####################
                # 属するエントリが1以上のカテゴリのみ列挙
                my %terms = (blog_id => $cfg{Blog_ID});
                # 管理者モードでなければステータスが'公開'のエントリのみカウント
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
                # 指定文字数でぶった切り
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
        $data .= "<input type=\"submit\" value=\"選択\"></form></center>";
        $data .= "<hr>";
    }
    
    ####################
    # 記事本文
    
    # 検索結果が0件の場合はメッセージ表示
    if (@entries <= 0) {
        $data .= "このｶﾃｺﾞﾘに属するｴﾝﾄﾘはありません";
    } else {
        my $i = 0;
        for my $entry (@entries){ # 結果のフェッチと表示
            my $title = &conv_euc_z2h($entry->title);
            $title = "untitled" if($title eq '');
            # 下書き／指定日かどうかを調べる
            my $ent_status = $entry->status;
            my $d_f;
            if ($ent_status == 1) {
                $d_f = '(下書き)';
            } elsif ($ent_status == 3) {
                $d_f = '(指定日)';
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
            if ($comment_cnt > 0 && $cfg{CommentColor} ne 'no'){ #コメント数を一覧に付加
                $data .= "<font color=\"$cfg{CommentColor}\">[$comment_cnt]</font>";
            }
            if ($ping_cnt > 0 && $cfg{TbColor} ne 'no'){ #トラックバック数を一覧に付加
                $data .= "<font color=\"$cfg{TbColor}\">[$ping_cnt]</font>";
            }
            $data .= "<br>";
        }
        
        # 最終ページの算出
        #if ($ttlcnt >= $cfg{DispNum}) {
        if ($ttlcnt > $cfg{DispNum}) {
            my $lastpage = int($ttlcnt / $cfg{DispNum});    # int()で小数点以下は切り捨て
            my $amari = $ttlcnt % $cfg{DispNum};            # 余りの算出
            if ($amari > 0) { $lastpage++ }                # あまりがあったら+1
            my $ttl = $lastpage;                        # 下のページ数表示用に値取得
            $lastpage--;                                # でもページは0から始まってるので-1（なんか間抜け）
            
            # ページ数表示
            my $here = $page + 1;
            $data .= "<center>$here/$ttl</center><hr>";
        
            # 引数用ページ数計算
            my $nextpage = $page + 1;
            my $prevpage = $page - 1;
            
            # 次、前、最初
            if ($rowid < $ttlcnt) {
                my $href = &make_href("", 0, $nextpage, 0, 0);
                if ($page == $lastpage - 1 && $amari > 0) {
                    $data .= "$nostr[9]<a href=\"$href\"$akstr[9]>次の$amari件 &gt;</a><br>";
                } else {
                    $data .= "$nostr[9]<a href=\"$href\"$akstr[9]>次の$cfg{DispNum}件 &gt;</a><br>";
                }
            }
            $rowid = $rowid - $rowcnt;
            if ($rowid > 0) {
                my $href = &make_href("", 0, $prevpage, 0, 0);
                $data .= "$nostr[7]<a href=\"$href\"$akstr[7]>&lt; 前の$cfg{DispNum}件</a><br>";
            }
            if ($page > 1) {
                my $href = &make_href("", 0, 0, 0, 0);
                $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>&lt;&lt; 最初の$cfg{DispNum}件</a><br>";
            }
            
            # 「最後」リンクの表示判定
            if ($page < $lastpage - 1) {
                my $href = &make_href("", 0, $lastpage, 0, 0);
                if ($amari > 0) {
                    $data .= "$nostr[8]<a href=\"$href\"$akstr[8]>最後の$amari件 &gt;&gt;</a><br>";
                } else {
                    $data .= "$nostr[8]<a href=\"$href\"$akstr[8]>最後の$cfg{DispNum}件 &gt;&gt;</a><br>";
                }
            }
        } else {
            $data .= "<center>1/1</center>";
        }

        # 最近のコメント一覧へのリンク
        if ($page == 0) {
            require MT::Comment;
            my $blog_comment_cnt = MT::Comment->count({ blog_id => $cfg{Blog_ID} });
            if ($blog_comment_cnt) {
                my $href = &make_href("recentcomment", 0, 0, 0, 0);
                $data .= "<hr><a href=\"$href\">最近のｺﾒﾝﾄ$cfg{RecentComment}件</a>";
            }
        }
    }
    
    # 管理者用URLへのリンクを表示する
    if ($cfg{AdminDoor} eq "yes"){
        $data .= "<hr>";
        my $href = &make_href("admindoor", 0, 0, 0);
        $data .= "<form method=\"post\" action=\"$href\">";
        $data .= "管理者用URLを取得<br>";
        $data .= "\AdminPasswordの値";
        $data .= "<br><input type=\"text\" name=\"pw_text\" istyle=3><br>";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"admindoor\">";
        $data .= "<input type=\"submit\" value=\"送信\">";
        if ($key){
            $data .= "<input type=hidden name=\"key\" value=\"$key\">";
        }
        $data .= "</form>";
        
        if ($admin_mode eq "yes"){
            $data .= '<font color="red">あなたは管理者用URLを入手済みです。このURLをﾌﾞｯｸﾏｰｸした後、速やかに「MT4i Manager」にて"AdminDoor"の値を"no"に変更してください。</font><br>';
        }
        if ($cfg{AdminPassword} eq "password"){
            $data .= '<font color="red">"AdminPassword"がﾃﾞﾌｫﾙﾄ値"password"から変更されていません。このままだと他人に管理者URLを推測される可能性が非常に高くなります。速やかに変更してください。</font><br>';
        }
    }
    
    #管理者用メニュー
    if ($admin_mode eq "yes"){
        $data .= "<hr>";

        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"[管]Entryの新規作成\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"entryform\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
        
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        if ($email_new_comments){
            $data .= "<input type=\"submit\" value=\"[管]ｺﾒﾝﾄのﾒｰﾙ通知を停止する\">";
        }else{
            $data .= "<input type=\"submit\" value=\"[管]ｺﾒﾝﾄのﾒｰﾙ通知を再開する\">";
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
# Sub Individual - 単記事ページの描画
########################################

sub individual {
    # 携帯電話からのアクセスかつアクセスキー有効の場合は$cfg{DispNum}を6以下にする
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
    # 記事の取得
    require MT::Entry;
    my $entry = MT::Entry->load($eid);

    # 検索結果が0件の場合はメッセージ表示してSTOP（有り得ないけどな）
    if (!$entry) {
        if ($hentities == 1) {
            $data = 'Entry ID \''.encode_entities($eid).'\' は不正です。';
        } else {
            $data = 'Entry ID \''.$eid.'\' は不正です。';
        }
        &errorout;
        exit;      # exitする
    }

    # 結果を変数に格納
    my $title = &conv_euc_z2h($entry->title);
    my $text = &conv_euc_z2h(MT->apply_text_filters($entry->text, $entry->text_filters));
    my $text_more = &conv_euc_z2h(MT->apply_text_filters($entry->text_more, $entry->text_filters));
    my $convert_breaks = $entry->convert_breaks;
    my $created_on = &conv_datetime($mt->version_number() >= 4.0 ? $entry->authored_on : $entry->created_on);
    my $comment_cnt = $entry->comment_count;
    my $ping_cnt = $entry->ping_count;
    # コメント投稿機能が強制OFFされている場合はallow_commentsをClosedに
    my $ent_allow_comments;
    if ($cfg{ArrowComments} == 1) {
        $ent_allow_comments = $entry->allow_comments;
    } else {
        $ent_allow_comments = 2;
    }
    my $ent_status = $entry->status;
    
    # 本文と追記を一つにまとめる
    if($text_more){
        $text = "<p>$text</p><p>$text_more</p>";
    }
    
    ####################
    # リンクのURLをchtmltrans経由に変換
    $text = &conv_redirect($text, $rowid, $eid);
    
    ####################
    # <img>タグソースURLのスラッシュを%2Fに変換
    if ($imk != 2) {
        $text = &img_url_conv($text);
    }
    
    ####################
    # 画像の除去（退避）
    
    my $href;
    
    # aタグを含めた除去、ALTの表示、画像へのリンク
    if ($imk == 2) {
        $text =~ s/<a[^>]*><img[^>]*src=\n*["']http:\/\/([^"'>]*)["'][^>]*alt=\n*["']([^"'>]*)["'][^>]*><\/a>/&lt;<a href="http:\/\/pic.to\/$1">画像：$2<\/a>&gt;/ig;
        $text =~ s/<a[^>]*><img[^>]*alt=\n*["']([^"'>]*)["'][^>]*src=\n*["']http:\/\/([^"'>]*)["'][^>]*><\/a>/&lt;<a href="http:\/\/pic.to\/$2">画像：$1<\/a>&gt;/ig;
        
        # imgタグのみの除去、ALTの表示、画像へのリンク
        $text =~ s/<img[^>]*src=\n*["']http:\/\/([^"'>]*)["'][^>]*alt=\n*["']([^"'>]*)["'][^>]*>/&lt;<a href="http:\/\/pic.to\/$1">画像：$2<\/a>&gt;/ig;
        $text =~ s/<img[^>]*alt=\n*["']([^"'>]*)["'][^>]*src=\n*["']http:\/\/([^"'>]*)["'][^>]*>/&lt;<a href="http:\/\/pic.to\/$2">画像：$1<\/a>&gt;/ig;
        
        # aタグを含めた除去、画像へのリンク
        $text =~ s/<a[^>]*><img[^>]*src=\n*["']http:\/\/([^"'>]*)["'][^>]*><\/a>/&lt;<a href="http:\/\/pic.to\/$1">画像<\/a>&gt;/ig;
        
        # imgタグのみの除去、画像へのリンク
        $text =~ s/<img[^>]*src=\n*["']http:\/\/([^"'>]*)["'][^>]*>/&lt;<a href="http:\/\/pic.to\/$1">画像<\/a>&gt;/ig;
    } else {
        $href = &make_href("image", $rowid, 0, $eid, 0);
        $text =~ s/<a[^>]*><img[^>]*src=\n*["']([^"'>]*)["'][^>]*alt=\n*["']([^"'>]*)["'][^>]*><\/a>/&lt;<a href="$href&amp;img=$1">画像：$2<\/a>&gt;/ig;
        $text =~ s/<a[^>]*><img[^>]*alt=\n*["']([^"'>]*)["'][^>]*src=\n*["']([^"'>]*)["'][^>]*><\/a>/&lt;<a href="$href&amp;img=$2">画像：$1<\/a>&gt;/ig;
        
        # imgタグのみの除去、ALTの表示、画像へのリンク
        $text =~ s/<img[^>]*src=\n*["']([^"'>]*)["'][^>]*alt=\n*["']([^"'>]*)["'][^>]*>/&lt;<a href="$href&amp;img=$1">画像：$2<\/a>&gt;/ig;
        $text =~ s/<img[^>]*alt=\n*["']([^"'>]*)["'][^>]*src=\n*["']([^"'>]*)["'][^>]*>/&lt;<a href="$href&amp;img=$2">画像：$1<\/a>&gt;/ig;
        
        # aタグを含めた除去、画像へのリンク
        $text =~ s/<a[^>]*><img[^>]*src=\n*["']([^"'>]*)["'][^>]*><\/a>/&lt;<a href="$href&amp;img=$1">画像<\/a>&gt;/ig;
        
        # imgタグのみの除去、画像へのリンク
        $text =~ s/<img[^>]*src=\n*["']([^"'>]*)["'][^>]*>/&lt;<a href="$href&amp;img=$1">画像<\/a>&gt;/ig;
    }
    
    ####################
    # タグ変換等
    if($convert_breaks eq '__default__' || ($convert_breaks ne '__default__' && $convert_breaks ne '0' && $convert_paras eq '__default__')) {
        # bqタグ部の色変更
        if ($cfg{BqColor}) {
            $text=~s/<blockquote>/<blockquote><font color="$cfg{BqColor}">/ig;
            $text=~s/<\/blockquote>/<\/font><\/blockquote>/ig;
        }
        # bqタグのpタグへの変換
        if ($cfg{BQ2P} eq "yes") {
            $text=~s/<blockquote>/<p>/ig;
            $text=~s/<\/blockquote>/<\/p>/ig;
        } else {
            # bqタグ周りの余計なbrタグ除去
            $text=~s/<br><br><blockquote>/<blockquote>/ig;
            $text=~s/<br><blockquote>/<blockquote>/ig;
            $text=~s/<\/blockquote><br><br>/<\/blockquote>/ig;
            $text=~s/<p><blockquote>/<blockquote>/ig;
            $text=~s/<\/blockquote><\/p>/<\/blockquote>/ig;
        }
        # pタグ周りの余計なbrタグ除去
        $text=~s/<br \/><br \/><p>/<p>/ig;
        $text=~s/<br \/><p>/<p>/ig;
        $text=~s/<\/p><br \/><br \/>/<\/p>/ig;
        $text=~s/<br \/><\/p>/<\/p>/ig;
        # ulタグ周りの余計なbrタグ除去
        $text=~s/<br \/><br \/><ul>/<ul>/ig;
        $text=~s/<br \/><ul>/<ul>/ig;
        $text=~s/<ul><br \/>/<ul>/ig;
        $text=~s/<\/ul><br \/><br \/>/<\/ul>/ig;
        # olタグ周りの余計なbrタグ除去
        $text=~s/<br \/><br \/><ol>/<ol>/ig;
        $text=~s/<br \/><ol>/<ol>/ig;
        $text=~s/<ol><br \/>/<ol>/ig;
        $text=~s/<\/ol><br \/><br \/>/<\/ol>/ig;
        # li閉じタグ除去
        $text=~s/<\/li>//ig;
    }
    
    ####################
    # 本文分割処理
    if (MT4i::Func::lenb_euc($text) > $cfg{SprtLimit}) {
        $text = &separate($text, $rowid);
    }
    
    ####################
    # 表示文字列生成
    $data .= "<h4>";
    
    # 記事一覧からの閲覧なら記事番号を振る
    if ($mode eq 'individual') {
        $data .= "$rowid.";
    }
    
    # 下書き／指定日かどうかを調べる
    my $d_f;
    if ($ent_status == 1) {
        $d_f = '(下書き)';
    } elsif ($ent_status == 3) {
        $d_f = '(指定日)';
    }
    
    $data .= "$d_f$title";
    
    # カテゴリ名の表示
    if ($cfg{IndividualCatLabelDisp} eq 'yes') {
        my $cat_label = &check_category($entry);
        $data .= "[$cat_label]";
    }
    
    if ($cfg{IndividualAuthorDisp} eq 'yes') {
        # Authorのnicknameがあれば、それを表示。無ければnameを表示する
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
    # 記事一覧からの閲覧なら記事番号を振る
    if ($mode eq 'individual') {
        # 総件数取得
        $ttlcnt = &get_ttlcnt;
        
        # エントリー数表示
        $data .= "<center>$rowid/$ttlcnt</center><hr>";
    } else {
        $data .= "<hr>";
    }
    
    #####################
    # Noneでは投稿も表示も無し、Openなら両方OK、Closedは表示のみ
    # $comment_cntの値 None=0,Open=1,Closed=2
    # MT3.2以降では Closed=2 が廃止された模様なので対応 2006/06/21
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
                # あいのり時はコメント参照できないように。
                # 何故って色々面倒だからさっ。
                $data .= "$nostr[8]<a href=\"$href\"$akstr[8]>ｺﾒﾝﾄ($comment_cnt)</a><hr>";
            }
        } elsif ($ent_allow_comments == 1) {
            if ($mode eq 'individual') {
                $href = &make_href("postform", $rowid, 0, $eid, 0);
            } elsif ($mode eq 'individual_rcm') {
                $href = &make_href("postform_rcm", $rowid, 0, $eid, 0);
            }
            $data .= "$nostr[8]<a href=\"$href\"$akstr[8]>ｺﾒﾝﾄ投稿</a><hr>";
            # ※モード「comment_lnk」の時はコメント投稿できない。
            # ※参照目的なんだからコメント書くこと無いでしょ、たぶん。
        }
    }
    
    # Trackback
    if ($ping_cnt > 0) {
        $href = &make_href("trackback", $rowid, 0, $eid);
        $data .= "$nostr[5]<a href=\"$href\"$akstr[5]>ﾄﾗｯｸﾊﾞｯｸ($ping_cnt)</a><hr>";
    }

    # 管理者のみ「Entry編集・消去」が可能
    if ($admin_mode eq "yes"){
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"[管]このEntryを編集\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"entryform\">";
        $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
        $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"[管]このEntryを削除\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"confirm_entry_del\">";
        $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
        $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
    }
    
    if ($mode eq 'individual') {
        # 記事一覧からの閲覧
        # 引数用エントリーNO算出
        my $nextno = $rowid + 1;
        my $prevno = $rowid - 1;
        
        # 引数用エントリーID算出（prevとnextが引っ繰り返っているので注意）
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
            # 非表示カテゴリが指定されている場合
            # 非表示カテゴリのリストをサブカテゴリも含めて取得する
            my @nondispcats = &get_nondispcats();
            
            # ぐるぐる回して非表示カテゴリと突合せ
            while ($next) {
                # エントリのカテゴリ取得
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
                # エントリのカテゴリ取得
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
            $data .= "$nostr[9]<a href=\"$href\"$akstr[9]>次の記事へ &gt;</a><br>";
        }
        if($rowid > 1) {
            $href = &make_href("individual", $prevno, 0, $previd, 0);
            $data .= "$nostr[7]<a href=\"$href\"$akstr[7]>&lt; 前の記事へ</a><br>";
        }
        # ページ数算出
        $page = int($no / $cfg{DispNum});    # int()で小数点以下は切り捨て
        
        $href = &make_href("", 0, $page, 0, 0);
        $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>一覧へ戻る</a>";
    } elsif ($mode eq 'individual_rcm') {
        # 最近コメント一覧からの閲覧
        $href = &make_href("recentcomment", 0, 0, 0, 0);
        $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>最近ｺﾒﾝﾄ一覧へ戻る</a>";
    } elsif ($mode eq 'individual_lnk') {
        # 記事中リンクからの閲覧
        $href = &make_href("individual", $rowid, 0, $ref_eid, 0);
        $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>ﾘﾝｸ元の記事へ戻る</a>";
    } elsif ($mode eq 'ainori') {
        # あいのり時はリファラへ戻る
        $href = $ENV{'HTTP_REFERER'};
        $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>ﾘﾝｸ元へ戻る</a>";
    }
    
    &htmlout;
}

########################################
# Sub Comment - コメント描画
########################################

sub comment {
    my $rowid = $no;
    
    ####################
    # entry idの取得
    require MT::Entry;
    my $entry = MT::Entry->load($eid);

    # 検索結果が0件の場合はメッセージ表示してSTOP（有り得ないけどな）
    if ($entry <= 0) {
        if ($hentities == 1) {
            $data = 'Entry ID \''.encode_entities($eid).'\' は不正です。';
        } else {
            $data = 'Entry ID \''.$eid.'\' は不正です。';
        }
        &errorout;
        exit;      # exitする
    }

    # 結果を変数に格納
    my $ent_title = &conv_euc_z2h($entry->title);
    my $ent_created_on = &conv_datetime($mt->version_number() >= 4.0 ? $entry->authored_on : $entry->created_on);
    my $ent_id = $entry->id;
    # コメント投稿機能が強制OFFされている場合はallow_commentsをClosedに
    my $ent_allow_comments;
    if ($cfg{ArrowComments} == 1) {
        $ent_allow_comments = $entry->allow_comments;
    } else {
        $ent_allow_comments = 2;
    }
    my $ent_status = $entry->status;
    
    ####################
    # コメントの取得
    my @comments;
    # 管理者モードではコメントを逆順表示する
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
        
        # 管理者のみ「コメント消去」等が可能
        if ($admin_mode eq "yes"){
            $text .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
            $text .= "<input type=\"submit\" value=\"[管]このｺﾒﾝﾄを削除\">";
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
    # タグ変換等
    if($convert_paras_comments eq '__default__'){
        # 改行のbrタグへの変換
        $text=~s/\r\n/<br>/g;
        $text=~s/\r/<br>/g;
        $text=~s/\n/<br>/g;
    }

    ####################
    # リンクのURLをchtmltrans経由に変換
    $text = &conv_redirect($text, $rowid, $eid);
    
    ####################
    # <_ahref>を<a href>に戻す
    $text=~s/_ahref/a href/g;
    
    ####################
    # 本文分割処理
    if (MT4i::Func::lenb_euc($text) > $cfg{SprtLimit}) {
        $text = &separate($text, $rowid);
    }
    
    ####################
    # 表示文字列生成
    $data .= "<h4>";
    if ($rowid) {
        $data .= "$rowid.";
    }
    if ($admin_mode eq "yes"){
        $data .= "$ent_title$ent_created_onへのｺﾒﾝﾄ(新しい順)</h4>";
    }else{
        $data .= "$ent_title$ent_created_onへのｺﾒﾝﾄ</h4>";
    }
    $data .= "$text<hr>";
    if ($ent_allow_comments == 1){
        if ($mode eq 'comment') {
            my $href = &make_href("postform", $rowid, 0, $eid, 0);
            $data .= "$nostr[8]<a href=\"$href\"$akstr[8]>ｺﾒﾝﾄ投稿</a><hr>";
        } elsif ($mode eq 'comment_rcm') {
            my $href = &make_href("postform_rcm", $rowid, 0, $eid, 0);
            $data .= "$nostr[8]<a href=\"$href\"$akstr[8]>ｺﾒﾝﾄ投稿</a><hr>";
        }
            # ※モード「comment_lnk」の時はコメント投稿できない。
            # ※参照目的なんだからコメント書くこと無いでしょ、たぶん。
    }
    my $href = &make_href("individual", $rowid, 0, $eid, 0);
    if ($mode eq 'comment') {
        $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>記事へ戻る</a>";
    } else {
        if ($mode eq 'comment_rcm') {
            $href =~ s/individual/individual_rcm/ig;
        } elsif ($mode eq 'comment_lnk') {
            $href = &make_href("individual_lnk", $rowid, 0, $eid, $ref_eid);
        }
        $data .= "$nostr[7]<a href=\"$href\"$akstr[7]>元記事を読む</a><hr>";
        if ($mode eq 'comment_rcm') {
            my $href = &make_href("recentcomment", 0, 0, 0, 0);
            $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>最近ｺﾒﾝﾄ一覧へ戻る</a>";
        } elsif ($mode eq 'comment_lnk') {
            my $href = &make_href("individual", $rowid, 0, $ref_eid, 0);
            $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>ﾘﾝｸ元の記事へ戻る</a>";
        }
    }

    &htmlout;
}

########################################
# Sub Recent_Comment - コメントまとめ読み
########################################

sub recent_comment {
    
    ####################
    # コメントの取得
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
    # 表示文字列生成
    $data .= "<h4>最近のｺﾒﾝﾄ$cfg{RecentComment}件</h4>";
    $data .= "$text<hr>";
    
    my $href = &make_href("", 0, 0, 0, 0);
    $data .= "<br>$nostr[0]<a href='$href'$akstr[0]>一覧へ戻る</a>";

    &htmlout;
}

########################################
# Sub Trackback - トラックバック表示
########################################

sub trackback {
    
    my $rowid = $no;
    
    ####################
    # トラックバックの取得
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
        # 管理者のみ「トラックバック削除」等が可能
        if ($admin_mode eq "yes"){
            $text .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
            $text .= "<input type=\"submit\" value=\"[管]このTBを削除\">";
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
    # リンクのURLをchtmltrans経由に変換
    $text = &conv_redirect($text, $rowid, $eid);
    
    ####################
    # <_ahref>を<a href>に戻す
    $text=~s/_ahref/a href/g;
    
    ####################
    # 表示文字列生成
    if (@tbpings < $cfg{RecentTB}){
        $cfg{RecentTB} = @tbpings;
    }
    
    $data .= "<h4>このEntryへの最近のﾄﾗｯｸﾊﾞｯｸ$cfg{RecentTB}件(新しい順)</h4>";
    $data .= "$text<hr>";
    
    my $href = &make_href("individual", $rowid, 0, $eid);
    $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>記事へ戻る</a>";
    
    &htmlout;
}

#############################################
# Sub Get_Entries - エントリの取得
# 第一引数 : オフセット
# 第二引数 : 取得個数
# 管理者の場合には、statusの限定解除
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
        # カテゴリ指定あり
        $arg{'join'} = [ 'MT::Placement', 'entry_id',
                 { blog_id => $cfg{Blog_ID}, category_id => $cat }, { unique => 1 } ];
    }
    
    if ($admin_mode eq "yes"){
        @ent = MT::Entry->load(\%terms, \%arg);
    } else {
        $terms{'status'} = 2;
        if ($cat == 0) {
            # カテゴリ指定なし
            if ($cfg{NonDispCat}) {
                # 非表示カテゴリ指定あり
                my %arg = (
                    direction => 'descend',
                );
                $arg{'sort'} = $mt->version_number() >= 4.0 ? 'authored_on' : 'created_on';
                my @entries = MT::Entry->load(\%terms, \%arg);
                
                # 非表示カテゴリのリストをサブカテゴリも含めて取得する
                my @nondispcats = &get_nondispcats();
                
                my $count = 1;
                foreach my $entry (@entries) {
                    # エントリのカテゴリ取得
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
                        # Non-Categoryは表示
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
                # 非表示カテゴリ指定なし
                @ent = MT::Entry->load(\%terms, \%arg);
            }
        } else {
            # カテゴリ指定あり
            @ent = MT::Entry->load(\%terms, \%arg);
        }
    }
    
    return @ent;
}

#############################################
# Sub Get_Comments - コメントの取得
# 第一引数 : エントリーID
# 第二引数 : 取得個数
# 第三引数 : ソート降順／昇順
# 第四引数 : visible値チェックの有無 1:有 0:無
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
    
    # 非表示カテゴリが指定されているか
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
                # Non-Categoryは表示
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
# Sub Get_Ttlcnt - 記事総数の取得
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
        #カテゴリなし
        if ($cfg{NonDispCat}) {
            # 非表示カテゴリ指定あり
            my @entries = MT::Entry->load(\%terms, \%arg);

            # 非表示カテゴリのリストをサブカテゴリも含めて取得する
            my @nondispcats = &get_nondispcats();
            
            my @ent;
            foreach my $entry (@entries) {
                # エントリのカテゴリ取得
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
                    # Non-Categoryは表示
                    push @ent, $entry;
                }
            }
            return @ent;
        } else {
            # 非表示カテゴリの指定なし
            return MT::Entry->count(\%terms, \%arg);
        }
    } else {
        #カテゴリあり
        $arg{'join'} = [ 'MT::Placement', 'entry_id',
                 { blog_id => $cfg{Blog_ID}, category_id => $cat }, { unique => 1 } ];
        return MT::Entry->count(\%terms, \%arg);
    }
}

##############################################
# Sub Make_Href - HREF文字列の作成
# 第一引数 : mode
# 第二引数 : no
# 第三引数 : page
# 第四引数 : eid
# 第五引数 : ref_eid
#
# 例外として、$modeが"post"の場合には
# idを出力しません
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
# Sub Image - 画像表示
########################################

sub image {
    # PerlMagick が無ければ画像縮小表示処理はしない
    if ($imk == 0){
        $img =~ s/\%2F/\//ig;
        if ($hentities == 1) {
            $data .='<p><img src="'.encode_entities($img).'"></p>';
        } else {
            $data .='<p><img src="'.$img.'"></p>';
        }
    }else{
        # /を%2Fに再エンコード
        $img =~ s/\//\%2F/ig;
        if ($hentities == 1) {
            $data .="<p><img src=\"./$cfg{MyName}?mode=img_cut&amp;id=$cfg{Blog_ID}&amp;img=".encode_entities($img)."\"></p>";
        } else {
            $data .="<p><img src=\"./$cfg{MyName}?mode=img_cut&amp;id=$cfg{Blog_ID}&amp;img=".$img."\"></p>";
        }
    }
    my $href = &make_href("individual", $no, 0, $eid, 0);
    $data .="$nostr[0]<a href=\"$href\"$akstr[0]>戻る</a>";
    
    &htmlout;
}

########################################
# Sub Image_Cut - 画像縮小表示
########################################

sub image_cut {
    $img =~ s/\%2F/\//ig;
    my $url = $img;
    $url =~ s/http:\/\///;
    my $host = substr($url, 0, index($url, "/"));
    my $path = substr($url, index($url, "/"));
    $data = "";

    ####################
    # ホスト名置換
    if ($host eq $cfg{Photo_Host_Original}){
        $host = $cfg{Photo_Host_Replace};
    }
    
    ####################
    # 画像読み込みをLWPモジュール使用に変更
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
    # vodafoneの特定機種に限りpng、それ以外はjpgに変換
    # サイズに関わらず、pngもしくはjpgに変換するように変更
    my $image = Image::Magick->new;
    $image->BlobToImage(@blob);
    
    # デジカメなどのアプリケーション情報の削除
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
    
    # 参考：http://deneb.jp/Perl/mobile/
    my $start_pos = 0;
    my $user_agent = $ENV{'HTTP_USER_AGENT'};
    my $cache_limit = -1024 + MT4i::Func::calc_cache_size( $user_agent );
    # 画像が既にキャッシュ許容範囲内なら縮小処理しない
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
# Sub Postform - コメント投稿フォーム
########################################

sub postform {
    my $rowid = $no;
    
    # Entry検索
    require MT::Entry;
    my $entry = MT::Entry->load($eid);

    # 検索結果が0件の場合はメッセージ表示してSTOP（有り得ないけどな）
    if ($entry <= 0) {
        if ($hentities == 1) {
            $data = 'Entry ID \''.encode_entities($eid).'\' は不正です。';
        } else {
            $data = 'Entry ID \''.$eid.'\' は不正です。';
        }
        &errorout;
        exit;      # exitする
    }

    # 結果を変数に格納
    my $ent_title = &conv_euc_z2h($entry->title);
    my $ent_created_on = &conv_datetime($mt->version_number >= 4.0 ? $entry->authored_on : $entry->created_on);

    ####################
    # 表示文字列生成
    $data = "<h4>";
    if ($rowid) {
        $data .= "$rowid.";
    }
    $data .= "$ent_title$ent_created_onへのｺﾒﾝﾄ投稿</h4><hr>";
    if ($mt->version_number() >= 3.0 && $cfg{ApproveComment} eq 'no') {
        $data .= "ｺﾒﾝﾄは投稿後、掲載を保留されます。<br>管理人による承諾後、掲載されます。<br>";
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
    $data .= "名前";
    if ($cfg{PostFromEssential} ne "yes"){
        $data .= "(省略可)";
    } else {
        $data .= '(入力必須)';
    }
    $data .= "<br><input type=text name=from><br>";
    $data .= "ﾒｰﾙｱﾄﾞﾚｽ";
    if ($cfg{PostMailEssential} ne "yes"){
        $data .= "(省略可)";
    } else {
        $data .= '(入力必須)';
    }
    $data .= "<br><input type=text name=mail><br>";
    $data .= "ｺﾒﾝﾄ";
    if ($cfg{PostTextEssential} ne "yes"){
        $data .= "(省略可)";
    } else {
        $data .= '(入力必須)';
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
    $data .= "「送信」を押してから書き込み完了まで多少時間がかかります。<br>環境によってはﾀｲﾑｱｳﾄが出ることがありますが、書き込みは完了しています。<br>「送信」の二度押しは絶対にしないで下さい。<br>";
    $data .= "<input type=hidden name=no value=$rowid>";
    $data .= "<input type=hidden name=eid value=$eid>";
    if ($key){
        $data .= "<input type=hidden name=\"key\" value=\"$key\">";
    }
    $data .= "<input type=submit value='送信'>";
    $data .= "</form>";
    $data .= "<hr>";
    if ($mode eq 'postform') {
        $href = &make_href("individual", $rowid, 0, $eid, 0);
    } elsif ($mode eq 'postform_rcm') {
        $href = &make_href("individual_rcm", $rowid, 0, $eid, 0);
    } elsif ($mode eq 'postform_lnk') {
        $href = &make_href("individual_lnk", $rowid, 0, $eid, 0);
    }
    $data .="$nostr[0]<a href='$href'$akstr[0]>戻る</a>";
    &htmlout;
}

########################################
# Sub Post - コメント投稿->表示処理
########################################
sub post {
    require MT::Comment;
    require MT::App;

    # SPAM対策
    # 本文が指定したパターンに適合したコメントを弾く
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
    
    # 投稿内容を一旦EUC-JPに変換
    if ($ecd == 1) {
        $post_from = encode("euc-jp",decode("shiftjis",$post_from));
        $post_text = encode("euc-jp",decode("shiftjis",$post_text));
    } else {
        $post_from = Jcode->new($post_from, 'sjis')->euc;
        $post_text = Jcode->new($post_text, 'sjis')->euc;
    }
    
    ####################
    # admin_helperをチェック(管理者モード時のみ)
    my $post_from_org = $post_from;
    if (($cfg{AdminHelper} eq 'yes') && ($admin_mode eq 'yes')){
        if ($post_from_org eq $cfg{AdminHelperID}){
            $post_from = $cfg{AdminHelperNM};
            $post_mail = $cfg{AdminHelperML};
        }
    }
    
    ####################
    # 必須入力項目をチェック
    # 名前,mail,textのどれも入力が無ければエラー
    if(((!$post_from)&&(!$post_text)&&(!$post_mail))||
       ((!$post_from)&&($cfg{PostFromEssential} eq "yes"))||
       ((!$post_mail)&&($cfg{PostMailEssential} eq "yes"))||
       ((!$post_text)&&($cfg{PostTextEssential} eq "yes")))
    {
        $data .="Error!<br>未入力項目があります.<br>";
        my $href = &make_href("postform", $rowid, 0, $eid, 0);
        $data .="$nostr[0]<a href='$href'$akstr[0]>戻る</a>";
        &errorout;
        #return;
        exit;
    }
    
    ####################
    # メールアドレスチェック
    if ($post_mail){
        unless($post_mail=~/^[\w\-+\.]+\@[\w\-+\.]+$/i){
            $data .="Error!<br>ﾒｰﾙｱﾄﾞﾚｽが不正です.<br>";
            my $href = &make_href("postform", $rowid, 0, $eid, 0);
            $data .="$nostr[0]<a href='$href'$akstr[0]>戻る</a>";
            &errorout;
            return;
        }
    }

    # 投稿された文字列の半角カナを全角に変換
    if ($ecd == 1) {
        Encode::JP::H2Z::h2z(\$post_from);
        Encode::JP::H2Z::h2z(\$post_text);
    } else {
        Jcode->new(\$post_from,'euc')->h2z;
        Jcode->new(\$post_text,'euc')->h2z;
    }

    # PublishCharsetに変換
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
    
    # 連続投稿防止
    # （直前のコメントと比較して同内容であれば
    #   連続投稿とみなしエラーとする。
    #   悪意ある連続投稿防止というよりは、
    #   タイムアウト後などの不作為の過失防止。）
    my @comments = get_comments($eid, 1, 'descend', 0);
    
    for my $tmp (@comments) {
        if ($post_from eq $tmp->author &&
            $post_mail eq $tmp->email &&
            $post_text eq $tmp->text) {
            $data .="Error!<br>同内容のｺﾒﾝﾄが既に投稿されています<hr>";
            my $href = &make_href("comment", $rowid, 0, $eid, 0);
            $data .="$nostr[0]<a href='$href'$akstr[0]>投稿されたｺﾒﾝﾄを確認する</a>";
            &errorout;
            return;
        }
    }
    
    # Entry ID、Entry Titleの取得
    require MT::Entry;
    my $entry = MT::Entry->load($eid);

    # 検索結果が0件の場合はメッセージ表示してSTOP（有り得ないけどな）
    if ($entry <= 0) {
        if ($hentities == 1) {
            $data = 'Entry ID \''.encode_entities($eid).'\' は不正です。';
        } else {
            $data = 'Entry ID \''.$eid.'\' は不正です。';
        }
        &errorout;
        exit;      # exitする
    }

    # DB更新
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
    
    # MT3.0以上ならvisible値設定
    if ($mt->version_number() >= 3.0) {
        # $cfg{ApproveComment}='yes'の場合には、書き込みと同時に掲載を承諾する
        if ($cfg{ApproveComment} eq 'yes') {
            $comment->visible(1);
        } else {
            $comment->visible(0);
        }
    }
    
    $comment->save
        or die $comment->errstr;

    ####################
    # MT3.0以上では、通知メール送信及びリビルドをバックグラウンドで行う
    if ($mt->version_number() >= 3.0) {
        require MT::Util;
        MT::Util::start_background_task(sub {
            # メール送信
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
                                        $entry->title . &conv_euc2icode(' への新しいコメント from MT4i')
                                );
                    my $charset;
                    # MT3.3以降で動作を変える
                    if ($mt->version_number() >= 3.3) {
                        $charset = $mt->{cfg}->MailEncoding || $mt->{cfg}->PublishCharset;
                    } else {
                        $charset = $mt->{cfg}->PublishCharset || 'iso-8859-1';
                    }
                    $head{'Content-Type'} = qq(text/plain; charset="$charset");
                    my $body = &conv_euc2icode('新しいコメントがウェブログ ') .
                                $blog->name  . ' ' .
                                &conv_euc2icode('のエントリー #') . $entry->id . " (" .
                                $entry->title . &conv_euc2icode(') にありました');
                    
                    # 元記事へのリンク作成
                    my $link_url = $entry->permalink;
                    
                    use Text::Wrap;
                    $Text::Wrap::cols = 72;
                    $body = Text::Wrap::wrap('', '', $body) . "\n$link_url\n\n" .
                    $body = $body . "\n$link_url\n\n" .
                      &conv_euc2icode('IPアドレス:') . ' ' . $comment->ip . "\n" .
                      &conv_euc2icode('名前:') . ' ' . $comment->author . "\n" .
                      &conv_euc2icode('メールアドレス:') . ' ' . $comment->email . "\n" .
                      &conv_euc2icode('URL:') . ' ' . $comment->url . "\n\n" .
                      &conv_euc2icode('コメント:') . "\n\n" . $comment->text . "\n\n" .
                      &conv_euc2icode("-- \nfrom MT4i v$version\n");
                    MT::Mail->send(\%head, $body);
                }
            }

            ####################
            # リビルド
            
            # Indexテンプレート
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
            
            # Archiveテンプレート
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
        # メール送信
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
                                    $entry->title . &conv_euc2icode(' への新しいコメント from MT4i')
                           );
                my $charset = $mt->{cfg}->PublishCharset || 'iso-8859-1';
                $head{'Content-Type'} = qq(text/plain; charset="$charset");
                my $body = &conv_euc2icode('新しいコメントがウェブログ ') .
                            $blog->name  . ' ' .
                            &conv_euc2icode('のエントリー #') . $entry->id . " (" .
                            $entry->title . &conv_euc2icode(') にありました');
                
                # 元記事へのリンク作成
                my $link_url = $entry->permalink;
                
                use Text::Wrap;
                $Text::Wrap::cols = 72;
                $body = Text::Wrap::wrap('', '', $body) . "\n$link_url\n\n" .
                $body = $body . "\n$link_url\n\n" .
                  &conv_euc2icode('IPアドレス:') . ' ' . $comment->ip . "\n" .
                  &conv_euc2icode('名前:') . ' ' . $comment->author . "\n" .
                  &conv_euc2icode('メールアドレス:') . ' ' . $comment->email . "\n" .
                  &conv_euc2icode('URL:') . ' ' . $comment->url . "\n\n" .
                  &conv_euc2icode('コメント:') . "\n\n" . $comment->text . "\n\n" .
                  &conv_euc2icode("-- \nfrom MT4i v$version\n");
                MT::Mail->send(\%head, $body);
            }
        }

        ####################
        # リビルド
        
        # Indexテンプレート
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
        
        # Archiveテンプレート
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

    # 画面表示
    if ($mt->version_number() >= 3.0 && $cfg{ApproveComment} eq 'no') {
        $data = "ｺﾒﾝﾄが投稿されましたが、掲載は保留されています。<br>管理人による承諾後、掲載されます。<hr>";
    } else {
        $data = "ｺﾒﾝﾄが投稿されました<hr>";
    }
    my $href;
    if ($mode eq 'post') {
        $href = &make_href("comment", $rowid, 0, $eid, 0);
    } elsif ($mode eq 'post_rcm') {
        $href = &make_href("comment_rcm", $rowid, 0, $eid, 0);
    } elsif ($mode eq 'post_lnk') {
        $href = &make_href("comment_lnk", $rowid, 0, $eid, 0);
    }
    $data .="$nostr[0]<a href='$href'$akstr[0]>戻る</a>";
    &htmlout;
}

########################################
# Sub entryform - 新規Entry/Entry編集 フォーム
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
        $data = "<h4>新規Entryの作成</h4><hr>";
        
        # 現在日時の取得
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
        
        $data = "<h4>Entryの編集</h4><hr>";
        
        # Entry検索
        require MT::Entry;
        my $entry = MT::Entry->load($eid);
        
        # 検索結果が0件の場合はメッセージ表示してSTOP（有り得ないけどな）
        if (!$entry) {
            if ($hentities == 1) {
                $data = 'Entry ID \''.encode_entities($eid).'\' は不正です。';
            } else {
                $data = 'Entry ID \''.$eid.'\' は不正です。';
            }
            &errorout;
            exit;      # exitする
        }
        
        # 編集なので、過去のデータを得る
        $org_title = &conv_euc_z2h($entry->title);
        $org_text = &conv_euc_z2h($entry->text);
        $org_text_more = &conv_euc_z2h($entry->text_more);
        $org_excerpt = &conv_euc_z2h($entry->excerpt);
        $org_keywords = &conv_euc_z2h($entry->keywords);
        if ($mt->version_number() >= 3.3) {
            require MT::Author;
            # AuthorNameをPublishCharsetに変換
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
        
        # タイトルをエンコード
        $org_title =~ s/&/&amp;/g;
        $org_title =~ s/ /&nbsp;/g;
        $org_title =~ s/\</&lt;/g;
        $org_title =~ s/\>/&gt;/g;
        # 本文をエンコード
        $org_text =~ s/&/&amp;/g;
        $org_text =~ s/\</&lt;/g;
        $org_text =~ s/\>/&gt;/g;
        # 追記をエンコード
        $org_text_more =~ s/&/&amp;/g;
        $org_text_more =~ s/\</&lt;/g;
        $org_text_more =~ s/\>/&gt;/g;
        # 概要をエンコード
        $org_excerpt =~ s/&/&amp;/g;
        $org_excerpt =~ s/\</&lt;/g;
        $org_excerpt =~ s/\>/&gt;/g;
        # キーワードをエンコード
        $org_keywords =~ s/&/&amp;/g;
        $org_keywords =~ s/\</&lt;/g;
        $org_keywords =~ s/\>/&gt;/g;
        # タグをエンコード
        $org_tags =~ s/&/&amp;/g;
        $org_tags =~ s/ /&nbsp;/g;
        $org_tags =~ s/\</&lt;/g;
        $org_tags =~ s/\>/&gt;/g;
    }
    
    ####################
    # 表示文字列生成
    my $href = &make_href("post", 0, 0, $eid, 0);
    $data .= "<form method=\"post\" action=\"$href\">";
    
    # カテゴリセレクタ
    my $cat_label;
    if ($eid){
        $cat_label = &check_category(MT::Entry->load($eid));
    }
    $data .= "ｶﾃｺﾞﾘ<br>";
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
    
    $data .= "ﾀｲﾄﾙ";
    $data .= "<br><input type=\"text\" name=\"entry_title\" value=\"$org_title\"><br>";
    $data .= "Entryの内容";
    $data .= "<br><textarea rows=\"4\" name=\"entry_text\">$org_text</textarea><br>";
    $data .= "Extended(追記)";
    $data .= "<br><textarea rows=\"4\" name=\"entry_text_more\">$org_text_more</textarea><br>";
    $data .= "Excerpt(概要)";
    $data .= "<br><textarea rows=\"4\" name=\"entry_excerpt\">$org_excerpt</textarea><br>";
    $data .= "ｷｰﾜｰﾄﾞ";
    $data .= "<br><textarea rows=\"4\" name=\"entry_keywords\">$org_keywords</textarea><br>";
    if ($mt->version_number() >= 3.3) {
        $data .= "ﾀｸﾞ(ｶﾝﾏで区切る)";
        $data .= "<br><input type=\"text\" name=\"entry_tags\" value=\"$org_tags\"><br>";
    }
    $data .= "投稿の状態<br>";
    $data .= "<select name=\"post_status\">";
    if (($eid && $org_ent_status == 1) || (!$eid && $blog->status_default == 1)) {
        $data .= "<option value=1 selected>下書き<br>";
        $data .= "<option value=2>公開<br>";
        if ($mt->version_number() >= 3.1) {
            $data .= "<option value=3>指定日<br>";
        }
    } elsif (($eid && $org_ent_status == 2) || (!$eid && $blog->status_default == 2)) {
        $data .= "<option value=1>下書き<br>";
        $data .= "<option value=2 selected>公開<br>";
        if ($mt->version_number() >= 3.1) {
            $data .= "<option value=3>指定日<br>";
        }
    } elsif (($eid && $org_ent_status == 3)) {
        $data .= "<option value=1>下書き<br>";
        $data .= "<option value=2>公開<br>";
        if ($mt->version_number() >= 3.1) {
            $data .= "<option value=3 selected>指定日<br>";
        }
    } else {
        $data .= "<option value=1>下書き<br>";
        $data .= "<option value=2 selected>公開<br>";
        if ($mt->version_number() >= 3.1) {
            $data .= "<option value=3>指定日<br>";
        }
    }
    $data .= "</select><br>";
    $data .= "<input type=\"hidden\" name=\"post_status_old\" value=\"".$org_ent_status."\">";
    
    $data .= "ｺﾒﾝﾄ<br>";
    $data .= "<select name=\"allow_comments\">";
    
    if (($eid && $org_ent_allow_comments == 0) || (!$eid && $blog->allow_comments_default == 0)) {
            $data .= "<option value=0 selected>なし<br>";
            $data .= "<option value=1>ｵｰﾌﾟﾝ<br>";
            $data .= "<option value=2>ｸﾛｰｽﾞ<br>";
    } elsif (($eid && $org_ent_allow_comments == 1) || (!$eid && $blog->allow_comments_default == 1)) {
            $data .= "<option value=0>なし<br>";
            $data .= "<option value=1 selected>ｵｰﾌﾟﾝ<br>";
            $data .= "<option value=2>ｸﾛｰｽﾞ<br>";
    } else {
            $data .= "<option value=0>なし<br>";
            $data .= "<option value=1>ｵｰﾌﾟﾝ<br>";
            $data .= "<option value=2 selected>ｸﾛｰｽﾞ<br>";
    }
    $data .= "</select><br>";
    
    $data .= "ﾄﾗｯｸﾊﾞｯｸを受けつける<br>";
    if (($eid && $org_ent_allow_pings) || (!$eid && $blog->allow_pings_default == 1)) {
        $data .= "<INPUT TYPE=checkbox name=\"allow_pings\" value=\"1\" CHECKED><br>";
    }else{
        $data .= "<INPUT TYPE=checkbox name=\"allow_pings\" value=\"1\"><br>";
    }
    
    ## テキストフォーマットのロード
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
    # ソート
    $text_filters = [ sort { $a->{filter_key} cmp $b->{filter_key} } @{ $text_filters } ];
    # 「なし」を追加
    unshift @{ $text_filters }, {
        filter_key => '0',
        filter_label => 'なし',
    };
    # 描画
    $data .= "ﾃｷｽﾄﾌｫｰﾏｯﾄ<br>";
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
        $data .= "公開日時<br>";
        $data .= "<input type=\"text\" name=\"entry_authored_on\" value=\"$org_authored_on\"><br>";
    } else {
        $data .= "作成日時<br>";
        $data .= "<input type=\"text\" name=\"entry_created_on\" value=\"$org_created_on\"><br>";
    }
    
    $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
    $data .= "<input type=\"hidden\" name=\"mode\" value=\"entry\">";
    $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
    $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
    if ($key){
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
    }
    $data .= "<input type=\"submit\" value=\"送信\">";
    $data .= "</form>";
    $data .= "<hr>";
    $href = &make_href("", 0, 0, 0, 0);
    $data .= "$nostr[0]<a href='$href'$akstr[0]>一覧へ戻る</a>";
    &htmlout;
}

########################################
# Sub Entry - 新規Entry投稿->表示処理
########################################
sub entry {
    my $rowid = $no;
    $no--;
    
    # 投稿内容を一旦EUC-JPに変換
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
    
    # 半角スペース'&nbsp;'をデコード
    $entry_title =~ s/&nbsp;/ /g;
    $entry_tags =~ s/&nbsp;/ /g;

    ####################
    # 必須入力項目をチェック
    # タイトル、テキストのどちらかの入力が無ければエラー
    if((!$entry_title)||(!$entry_text))
    {
        $data .="Error!<br>未入力項目があります。「ﾀｲﾄﾙ」と「Entryの内容」は必須です。<br>";
        my $href = &make_href("entryform", 0, 0, $eid, 0);
        $data .="$nostr[0]<a href=\"$href\"$akstr[0]>戻る</a>";
        &errorout;
        return;
    }
    # 作成日時あるいは公開日時の入力が無ければエラー
    if ($mt->version_number() >= 4.0) {
        if (!$entry_authored_on) {
            $data .="Error!<br>未入力項目があります。「公開日時」は必須です。<br>";
            my $href = &make_href("entryform", 0, 0, $eid, 0);
            $data .="$nostr[0]<a href=\"$href\"$akstr[0]>戻る</a>";
            &errorout;
            return;
        }
    } else {
        if (!$entry_created_on) {
            $data .="Error!<br>未入力項目があります。「作成日時」は必須です。<br>";
            my $href = &make_href("entryform", 0, 0, $eid, 0);
            $data .="$nostr[0]<a href=\"$href\"$akstr[0]>戻る</a>";
            &errorout;
            return;
        }
    }
    require MT::Author;
    # AuthorNameをPublishCharsetに変換
    if ($conv_in ne 'euc') {
        if ($conv_in eq 'utf8' && $ecd == 1) {
            $cfg{AuthorName} = encode("shiftjis",decode("euc-jp",$cfg{AuthorName}));
            $cfg{AuthorName} = encode("utf8",decode("cp932",$cfg{AuthorName}));
        } else {
            $cfg{AuthorName} = Jcode->new($cfg{AuthorName}, 'euc')->$conv_in();
        }
    }
    if (!$cfg{AuthorName}) {
        $data = 'MT4i Manager にて Author名（AuthorName）が設定されていません。';
        &errorout;
        exit;      # exitする
    }
    my $author = MT::Author->load({ name => $cfg{AuthorName} });
    if (!$author) {
        # AuthorNameをEUC-JPに戻す
        if ($conv_in eq 'utf8' && $ecd == 1) {
            $cfg{AuthorName} = encode("cp932",decode("utf8",$cfg{AuthorName}));
            $cfg{AuthorName} = encode("euc-jp",decode("shiftjis",$cfg{AuthorName}));
        } else {
            $cfg{AuthorName} = Jcode->new($cfg{AuthorName}, $conv_in)->euc;
        }
        $data = "\"$cfg{AuthorName}\"がAuthorとして登録されていません。<br>";
        &errorout;
        exit;      # exitする
    }
    
    # 投稿された文字列の半角カナを全角に変換
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
    # PublishCharsetに変換
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
        $data = "Entryは修正されました<hr>";
    }else{
        $data = "新規Entryが作成されました<hr>";
    }
    
    ####################
    # 保存のステータスがリリースか、あるいは編集前のステータスがリリースの場合のみ
    # エントリー及びインデックスのリビルドを行い、ピングを送信する。
    if ($post_status == MT::Entry::RELEASE() || $post_status_old eq MT::Entry::RELEASE()) {
        # MT3.0以上では、リビルド及び更新ping送信をバックグラウンドで行う
        if ($mt->version_number() >= 3.0) {
            require MT::Util;
            MT::Util::start_background_task(sub {
                # リビルド
                $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                    or die $mt->errstr;
                
                ####################
                # 更新ping送信
                # 保存のステータスがリリースの場合のみping送信
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
            # リビルド
            $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                or die $mt->errstr;
            
            ####################
            # 更新ping送信
            # 保存のステータスがリリースの場合のみping送信
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
    $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>一覧へ戻る</a>";
    &htmlout;
}

########################################
# Sub Entry_del - Entry削除
########################################
sub entry_del {
    
    my $rowid = $no;
    $no--;
    
    require MT::Entry;
    my $entry = MT::Entry->load($eid);
    if (!$entry) {
        if ($hentities == 1) {
            $data = 'entry_del::Entry ID \''.encode_entities($eid).'\' は不正です。';
        } else {
            $data = 'entry_del::Entry ID \''.$eid.'\' は不正です。';
        }
        &errorout;
        exit;      # exitする
    }
    
    $entry->remove;
    
    ####################
    # MT3.0以上では、リビルドをバックグラウンドで行う
    if ($mt->version_number() >= 3.0) {
        require MT::Util;
        MT::Util::start_background_task(sub {
            # リビルド
            #$mt->rebuild_indexes( Blog => $blog )
            #    or die $mt->errstr;
            $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                or die $mt->errstr;
        });
    } else {
        # リビルド
        #$mt->rebuild_indexes( Blog => $blog )
        #    or die $mt->errstr;
        $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
            or die $mt->errstr;
    }
    
    $data = "Entryが削除されました<hr>";
    my $href = &make_href("", 0, 0, 0, 0);
    $data .= "$nostr[0]<a href='$href'$akstr[0]>一覧へ戻る</a>";
    &htmlout;
}

########################################
# Sub Comment_del - コメント削除
########################################
sub comment_del {
    
    my $rowid = $no;
    $no--;
    
    ####################
    # commentを探す
    require MT::Comment;
    my $comment = MT::Comment->load($page);    # コメント番号は$pageで渡す
    if (!$comment) {
        if ($hentities == 1) {
            $data = "comment_del::Comment ID '".encode_entities($page)."' は不正です。";
        } else {
            $data = "comment_del::Comment ID '".$page."' は不正です。";
        }
        &errorout;
        exit;      # exitする
    }
    $comment->remove()
        or die $comment->errstr;
    
    #このcommentが属するEntryを探す
    require MT::Entry;
    my $entry = MT::Entry->load($comment->entry_id);
    if (!$entry) {
        $data = "comment_del::Entry ID '".$comment->entry_id."' は不正です。";
        &errorout;
        exit;      # exitする
    }
    
    ####################
    # MT3.0以上では、リビルドをバックグラウンドで行う
    if ($mt->version_number() >= 3.0) {
        require MT::Util;
        MT::Util::start_background_task(sub {
            # リビルド
            #$mt->rebuild_indexes( Blog => $blog )
            #    or die $mt->errstr;
            $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                or die $mt->errstr;
        });
    } else {
        # リビルド
        #$mt->rebuild_indexes( Blog => $blog )
        #    or die $mt->errstr;
        $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
            or die $mt->errstr;
    }
    
    $data = "ｺﾒﾝﾄが削除されました<hr>";
    my $href = &make_href("comment", $rowid, 0, $eid, 0);
    $data .= "$nostr[0]<a href=\'$href\'$akstr[0]>ｺﾒﾝﾄ一覧へ戻る</a>";
    &htmlout;
}

########################################
# Sub Trackback_del - トラックバック削除
########################################
sub trackback_del {
    
    my $rowid = $no;
    $no--;
    
    ####################
    # pingを探す
    require MT::TBPing;
    my $tbping = MT::TBPing->load($page);    # トラックバック番号は$pageで渡す
    if (!$tbping) {
        if ($hentities == 1) {
            $data = "trackback_del::MTPing ID '".encode_entities($page)."' は不正です。";
        } else {
            $data = "trackback_del::MTPing ID '".$page."' は不正です。";
        }
        &errorout;
        exit;      # exitする
    }
    $tbping->remove()
        or die $tbping->errstr;
    
    #このtbpingが属するTrackbackを探す
    require MT::Trackback;
    my $trackback = MT::Trackback->load($tbping->tb_id);
    if (!$trackback) {
        $data = "trackback_del::Trackback ID '".$tbping->tb_id."' は不正です。";
        &errorout;
        exit;      # exitする
    }
    
    #このTrackbackが属するEntryを探す
    require MT::Entry;
    my $entry = MT::Entry->load($trackback->entry_id);
    if (!$entry) {
        $data = "trackback_del::Entry ID '".$trackback->entry_id."' は不正です。";
        &errorout;
        exit;      # exitする
    }
    
    ####################
    # MT3.0以上では、リビルドをバックグラウンドで行う
    if ($mt->version_number() >= 3.0) {
        require MT::Util;
        MT::Util::start_background_task(sub {
            # リビルド
            #$mt->rebuild_indexes( Blog => $blog )
            #    or die $mt->errstr;
            $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                or die $mt->errstr;
        });
    } else {
        # リビルド
        #$mt->rebuild_indexes( Blog => $blog )
        #    or die $mt->errstr;
        $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
            or die $mt->errstr;
    }
    
    $data = "ﾄﾗｯｸﾊﾞｯｸが削除されました<hr>";
    my $href = &make_href("trackback", $rowid, 0, $eid, 0);
    $data .= "$nostr[0]<a href=\'$href\'$akstr[0]>ﾄﾗｯｸﾊﾞｯｸ一覧へ戻る</a>";
    &htmlout;
}

########################################
# Sub Trackback_ipban - このIPからのトラックバックを禁止＆全削除
########################################
sub trackback_ipban {
    
    my $rowid = $no;
    $no--;
    
    ####################
    # pingを探す
    require MT::TBPing;
    my $tbping = MT::TBPing->load($page);    # トラックバック番号は$pageで渡す
    if (!$tbping) {
        if ($hentities == 1) {
            $data = "trackback_ipban::MTPing ID '".encode_entities($page)."' は不正です。";
        } else {
            $data = "trackback_ipban::MTPing ID '".$page."' は不正です。";
        }
        &errorout;
        exit;      # exitする
    }
    
    require MT::IPBanList;
    my $ban = MT::IPBanList->new;
    $ban->blog_id($blog->id);
    $ban->ip($tbping->ip);
    $ban->save
        or die $ban->errstr;
    
    ####################
    # そのIPから送信されたトラックバックを全て探す
    my @tbpings = MT::TBPing->load(
            { blog_id => $cfg{Blog_ID}, ip => $tbping->ip});    
    
    for my $tbping (@tbpings) {
        
        #このtbpingが属するTrackbackを探す
        require MT::Trackback;
        my $trackback = MT::Trackback->load($tbping->tb_id);
        if (!$trackback) {
            $data = "trackback_ipban::Trackback ID '".$tbping->tb_id."' は不正です。";
            &errorout;
            exit;      # exitする
        }
        
        #このTrackbackが属するEntryを探す
        require MT::Entry;
        my $entry = MT::Entry->load($trackback->entry_id);
        if (!$entry) {
            $data = "trackback_ipban::Entry ID '".$trackback->entry_id."' は不正です。";
            &errorout;
            exit;      # exitする
        }
        
        $data .= &conv_euc_z2h($tbping->excerpt)."<hr>";
        
        # トラックバックping削除
        $tbping->remove()
            or die $tbping->errstr;

        ####################
        # MT3.0以上では、リビルドをバックグラウンドで行う
        if ($mt->version_number() >= 3.0) {
            require MT::Util;
            MT::Util::start_background_task(sub {
                # entryのリビルド
                $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                    or die $mt->errstr;
            });
        } else {
            # entryのリビルド
            $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                or die $mt->errstr;
        }
    }
    
    $data = "IPを禁止ﾘｽﾄに追加し、".@tbpings."件のﾄﾗｯｸﾊﾞｯｸを削除しました。<hr>";
    my $href = &make_href("trackback", $rowid, 0, $eid ,0);
    $data .= "$nostr[0]<a href=\'$href\'$akstr[0]>ﾄﾗｯｸﾊﾞｯｸ一覧へ戻る</a>";
    &htmlout;
    
    ####################
    # MT3.0以上では、リビルドをバックグラウンドで行う
    if ($mt->version_number() >= 3.0) {
        require MT::Util;
        MT::Util::start_background_task(sub {
            # indexのリビルド
            $mt->rebuild_indexes( Blog => $blog )
                or die $mt->errstr;
        });
    } else {
        # indexのリビルド
        $mt->rebuild_indexes( Blog => $blog )
            or die $mt->errstr;
    }
}

########################################
# Sub Comment_ipban - このIPからのコメントを禁止＆全削除
########################################
sub comment_ipban {
    
    my $rowid = $no;
    $no--;
    
    ####################
    # commentを探す
    require MT::Comment;
    my $comment = MT::Comment->load($page);    # コメント番号は$pageで渡す
    if (!$comment) {
        if ($hentities == 1) {
            $data = "comment_ipban::Comment ID '".encode_entities($page)."' は不正です。";
        } else {
            $data = "comment_ipban::Comment ID '".$page."' は不正です。";
        }
        &errorout;
        exit;      # exitする
    }
    
    require MT::IPBanList;
    my $ban = MT::IPBanList->new;
    $ban->blog_id($blog->id);
    $ban->ip($comment->ip);
    $ban->save
        or die $ban->errstr;
    
    ####################
    # そのIPから送信されたコメントを全て探す
    my @comments = MT::Comment->load(
            { blog_id => $cfg{Blog_ID}, ip => $comment->ip});
    
    for my $comment (@comments) {
        
        require MT::Entry;
        my $entry = MT::Entry->load($comment->entry_id);
        if (!$entry) {
            $data = "comment_ipban::Entry ID '".$comment->entry_id."' は不正です。";
            &errorout;
            exit;      # exitする
        }
        
        # コメント削除
        $comment->remove()
            or die $comment->errstr;
        
        ####################
        # MT3.0以上では、リビルドをバックグラウンドで行う
        if ($mt->version_number() >= 3.0) {
            require MT::Util;
            MT::Util::start_background_task(sub {
                # entryのリビルド
                $mt->rebuild_entry( Entry => $entry,, BuildDependencies => 1 )
                    or die $mt->errstr;
            });
        } else {
            # entryのリビルド
            $mt->rebuild_entry( Entry => $entry, BuildDependencies => 1 )
                or die $mt->errstr;
        }
    }
    
    $data = "IPを禁止ﾘｽﾄに追加し、".@comments."件のｺﾒﾝﾄを削除しました。<hr>";
    my $href = &make_href("comment", $rowid, 0, $eid, 0);
    $data .= "$nostr[0]<a href=\'$href\'$akstr[0]>ｺﾒﾝﾄ一覧へ戻る</a>";
    &htmlout;
    
    ####################
    # MT3.0以上では、リビルドをバックグラウンドで行う
    if ($mt->version_number() >= 3.0) {
        require MT::Util;
        MT::Util::start_background_task(sub {
            # indexのリビルド
            $mt->rebuild_indexes( Blog => $blog )
                or die $mt->errstr;
        });
    } else {
        # indexのリビルド
        $mt->rebuild_indexes( Blog => $blog )
            or die $mt->errstr;
    }
}

########################################
# Sub Email_comments - コメントのメール通知制御
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
        $data = "ｺﾒﾝﾄのﾒｰﾙ通知を停止しました。<hr>";
    }else{
        $data = "ｺﾒﾝﾄのﾒｰﾙ通知を再開しました。<hr>";
    }
    
    my $href = &make_href("", 0, $page, 0, 0);
    $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>一覧へ戻る</a>";
    &htmlout;

}

########################################
# Sub Confirm - 各種確認
########################################
sub confirm {
    
    my $rowid = $no;
    
    # コメントIDは$pageで受け渡し
    if ($mode eq "confirm_comment_del"){
        
        require MT::Comment;
        my $comment = MT::Comment->load($page);    # コメント番号は$pageで渡す
        if (!$comment) {
            if ($hentities == 1) {
                $data = "confirm_comment_del::Comment ID '".encode_entities($page)."' は不正です。";
            } else {
                $data = "confirm_comment_del::Comment ID '".$page."' は不正です。";
            }
            &errorout;
            exit;      # exitする
        }
        $data .="本当に以下のコメントを削除してよろしいですか？<br>";
        
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"キャンセルする\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"comment\">";
        $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
        $data .= "<input type=\"hidden\" name=\"page\" value=\"$page\">";
        $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"削除する\">";
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
                $data = "confirm_entry_del::Entry ID '".encode_entities($eid)."' は不正です。";
            } else {
                $data = "confirm_entry_del::Entry ID '".$eid."' は不正です。";
            }
            &errorout;
            exit;      # exitする
        }
        
        require MT::Author;
        my $author = MT::Author->load({ id => $entry->author_id });    
        my $author_name = "";
        if ($author) {
            $author_name = &conv_euc_z2h($author->name);
        }
        
        $data .="本当に以下のEntryを削除してよろしいですか？<br>";
        
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"キャンセルする\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"individual\">";
        $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
        $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"削除する\">";
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
        my $tbping = MT::TBPing->load($page);    # トラックバック番号は$pageで渡す
        if (!$tbping) {
            if ($hentities == 1) {
                $data = "confirm_trackback_del::MTPing ID '".encode_entities($page)."' は不正です。";
            } else {
                $data = "confirm_trackback_del::MTPing ID '".$page."' は不正です。";
            }
            &errorout;
            exit;      # exitする
        }
        
        $data .="本当に以下のTBを削除してよろしいですか？<br>";

        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"キャンセルする\">";
        $data .= "<input type=\"hidden\" name=\"id\" value=\"$cfg{Blog_ID}\">";
        $data .= "<input type=\"hidden\" name=\"mode\" value=\"trackback\">";
        $data .= "<input type=\"hidden\" name=\"no\" value=\"$rowid\">";
        $data .= "<input type=\"hidden\" name=\"page\" value=\"$page\">";
        $data .= "<input type=\"hidden\" name=\"eid\" value=\"$eid\">";
        $data .= "<input type=\"hidden\" name=\"key\" value=\"$key\">";
        $data .= "</form>";
        $data .= "<form method=\"POST\" action=\"$cfg{MyName}\">";
        $data .= "<input type=\"submit\" value=\"削除する\">";
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
        $data .="confirm::mode '".$mode."' は不正です。<br>";
    }
    
    &htmlout;
}

########################################
# Sub Admindoor - 管理者用URLを表示
########################################
sub admindoor {
    my $href;
    if ($pw_text eq $cfg{AdminPassword}){
        $data .= '管理者用URLは';
        $href = &make_href("", 0, 0, 0, 0);
        $href .= '&key='.MT4i::Func::enc_crypt($cfg{AdminPassword}.$cfg{Blog_ID});
        $data .= "<a href=\"$href\">こちら</a>";
        $data .= 'です。ﾘﾝｸ先をﾌﾞｯｸﾏｰｸした後、速やかに「mt4i Manager」にて"AdminDoor"の値を"no"に変更してください。<br>';
    }else{
        $data .= "ﾊﾟｽﾜｰﾄﾞが違います<hr>";
    }
    $key = "";
    $href = &make_href("", 0, 0, 0, 0);
    $data .= "$nostr[0]<a href='$href'$akstr[0]>戻る</a>";
    &htmlout;
}

########################################
# Sub Separate - 単記事・コメント本文の分割
########################################

sub separate {
    my $text = $_[0];
    my $rowid = $_[1];
    
    # 区切り文字列を配列に格納しておく
    my @sprtstrlist = split(",",$cfg{SprtStr});
    
    # 本文のバイト数を求めておく
    my $maxlen = MT4i::Func::lenb_euc($text);
    
    # 初回に分割位置を決め、$sprtbyteへ格納
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
            
            # 区切り文字列の検出
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
            
            # 分割位置を$sprtbyteに格納
            if ($sprtstart < $maxlen) {
                $sprtbyte .= ",$sprtstart";
            }
            $i = $sprtstart + 1;
        }
    }
    
    # $sprtbyteを読み取る
    my @argsprtbyte = split(/,/, $sprtbyte);
    my $sprtstart = $argsprtbyte[$sprtpage - 1];
    my $sprtend;
    if ($sprtpage - 1 < $#argsprtbyte) {
        $sprtend = $argsprtbyte[$sprtpage] - $sprtstart;
    } else {
        $sprtend = $maxlen - $sprtstart;
    }
    
    ####################
    # 本文文字列生成
    
    my $tmptext = "";
    my $href = &make_href($mode, $rowid, 0, $eid, 0);
    
    # まずは記事本文切抜き
    my $text = MT4i::Func::midb_euc($text, $sprtstart, $sprtend);
    
    ##### 足りないタグを補ってみる #####
    my $cnt_tag_o;
    my $cnt_tag_c;
    # ULタグ
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
    # OLタグ
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
    # BLOCKQUOTEタグ
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
    # FONTタグ
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
    
    # ページリンク（上）
    $tmptext .= "&lt; ﾍﾟｰｼﾞ移動:";
    for (my $i = 1; $i <= $#argsprtbyte + 1; $i++)  {
        if ($i == $sprtpage) {
            $tmptext .= " $i";
        } else {
            $tmptext .= " <a href=\"$href&amp;sprtpage=$i&amp;sprtbyte=$sprtbyte\">$i</a>";
        }
    }
    $tmptext .= " &gt;<br>";
    
    # 記事本文
    $tmptext .= $text;
    
    # ページリンク（下）
    $tmptext .= "<br>&lt; ﾍﾟｰｼﾞ移動:";
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
# Sub Conv_euc_z2h - →EUC-JP／全角→半角変換
########################################

sub conv_euc_z2h {
    my $tmpstr = $_[0];

    return $tmpstr unless $tmpstr;

    # 第一引数をEUC-JPに変換
    if ($conv_in ne "euc") {
        if ($conv_in eq "utf8" && $ecd == 1) {
            $tmpstr = encode("cp932",decode("utf8",$tmpstr));
            $tmpstr = encode("euc-jp",decode("shiftjis",$tmpstr));
        } else {
            $tmpstr = Jcode->new($tmpstr, $conv_in)->euc;
        }
    }
    
    # 表示文字列の全角文字を半角に変換
    if ($cfg{Z2H} eq "yes") {
        if ($ecd == 1) {
            Encode::JP::H2Z::z2h(\$tmpstr);
            $tmpstr = Jcode->new($tmpstr,'euc')->tr('Ａ-Ｚａ-ｚ０-９／！？（）＝＆', 'A-Za-z0-9/!?()=&');
        } else {
            $tmpstr = Jcode->new($tmpstr,'euc')->z2h->tr('Ａ-Ｚａ-ｚ０-９／！？（）＝＆', 'A-Za-z0-9/!?()=&');
        }
    }
    return $tmpstr;
}

########################################
# Sub Img_Url_Conv - 画像URLのスラッシュを%2Fに変換
########################################

sub img_url_conv {
    my $tmpstr = $_[0];
    my $str = "";
    
    # ループしながら<img>タグ内URLの置換
    while ($tmpstr =~ /(<img(?:[^"'>]|"[^"]*"|'[^']*')*src=)("[^"]*"|'[^']*')((?:[^"'>]|"[^"]*"|'[^']*')*>)/i) {
        my $front = $` . $1;
        my $url = $2;
        my $end = $3 . $';
        
        # ダブル・シングルクォーテーションを取り除く
        $url =~ s/["']//g;
        
        # "/"→"%2F"
        $url =~ s/\//\%2F/g;
        
        # ダブルクォーテーションを補いつつ結合
        $str .= "$front\"" . $url;
        $tmpstr = "\"$end";
    }
    $str .= $tmpstr;
    return $str;
}

########################################
# Sub Conv_Redirect - リンクのURLをリダイレクタ経由に変換
########################################

sub conv_redirect {
    my $tmpstr = $_[0];
    my $ref_rowid = $_[1];
    my $ref_eid = $_[2];
    my $str = "";
    
    # ループしながらURLの置換
    while ($tmpstr =~ /(<a(?:[^"'>]|"[^"]*"|'[^']*')*href=)("[^"]*"|'[^']*')((?:[^"'>]|"[^"]*"|'[^']*')*>)/i) {
        my $front = $` . $1;
        my $url = $2;
        my $end = $3;
        my $backward = $';
        my $tmpfront = $1;
        my $tmpend = $3;
        my $lnkstr = "";

        my $title;
        
        # title属性を取り出す
        if ($tmpfront =~ /title=/i) {
            my $tmpstr = $tmpfront;
            $tmpstr =~ s/.*<a(?:[^"'>]|"[^"]*"|'[^']*')*title=("[^"]*"|'[^']*')(?:[^"'>]|"[^"]*"|'[^']*')*\Z/$1/i;
            $title = $tmpstr;
        } elsif ($tmpend =~ /title=/i) {
            my $tmpstr = $tmpend;
            $tmpstr =~ s/\A.*(?:[^"'>]|"[^"]*"|'[^']*')*title=("[^"]*"|'[^']*')(?:[^"'>]|"[^"]*"|'[^']*')*>/$1/i;
            $title = $tmpstr;
        }
        # ダブル・シングルクォーテーションを取り除く
        $title =~ s/["']//g;
        $url =~ s/["']//g;
        
        if ($title !~ /$cfg{ExitChtmlTrans}/) {
            my $tmpurl = &make_href("redirect", $ref_rowid, 0, 0, $ref_eid);
            
            # "/"→"%2F"
            $url =~ s!/!\%2F!g;
            
            # "&"→"%26"
            $url =~ s/\&/\%26/g;
            
            $url = $tmpurl . '&amp;url=' . $url;
        } else {
            # 携帯対応マーク
            $lnkstr = $ExitChtmlTransStr;
        }
        # ダブルクォーテーションを補いつつ結合
        $str .= "$front\"" . $url;
        $tmpstr = "\"$end" . $lnkstr . $backward;
        
    }
    $str .= $tmpstr;

    # title、target属性の削除（バイト数の無駄）
    $str =~ s/ target=["'][^"']*["']//ig;
    $str =~ s/ title=["'][^"']*["']//ig;
    
    return $str;
}

########################################
# Sub Redirector - リダイレクタ
########################################

sub redirector {
    # URLを変換
    my ($lnkstr,$lnkurl) = &chtmltrans($redirect_url);
    
    # モバイル用のURLが見つかったか判定
    if ($lnkstr) {
        # モバイル用URLが見つかった場合
        $data .= '<p>別のｻｲﾄへｼﾞｬﾝﾌﾟしようとしています。';
        $data .= '携帯電話／ﾓﾊﾞｲﾙ機器用のURLが見つかりました。</p>';
        $data .= "<p>↓ｸﾘｯｸ<br>$lnkstr<a href=\"$lnkurl\">$lnkurl</a></p>";
        $data .= '<p>下記が元のURLになります。';
        $data .= '上記で上手く表示できない場合、下記URLをお試し下さい。</p>';
        $data .= "<p>↓ｸﾘｯｸ<br><a href=\"$redirect_url\">$redirect_url</a></p>";
    } else {
        # モバイル用URLが見つからなかった場合
        $data .= '<p>別のｻｲﾄへｼﾞｬﾝﾌﾟしようとしています。</p>';
        $data .= "<p>↓ｸﾘｯｸ<br><a href=\"$redirect_url\">$redirect_url</a></p>";
        $data .= '<p>上記URLのｻｲﾄは携帯電話で正しく表示できないかもしれませんが、';
        $data .= '下記URLであれば表示できるかもしれません。</p>';
        $data .= "<p>↓ｸﾘｯｸ<br><a href=\"$lnkurl\">$lnkurl</a></p>";
    }
    $data .= "<hr>";
    my $href = &make_href("individual", $no, 0, $ref_eid, 0);
    $data .= "$nostr[0]<a href=\"$href\"$akstr[0]>戻る</a>";
    $data .= "<hr>";
    &htmlout;
}

########################################
# Sub Chtmltrans - リンクのURLをchtmltrans経由その他に変換
# 参考：Perlメモ→http://www.din.or.jp/~ohzaki/perl.htm#HTML_Tag
########################################

sub chtmltrans {
    my $url = $_[0];
    my $lnkstr = "";
    
    if ($url =~ m/.*http:\/\/www.amazon.co.jp\/exec\/obidos\/ASIN\/.*/g) {
        # Amazon個別商品リンクならi-mode対応へ変換
        $url =~ s!exec/obidos/ASIN/!gp/aw/rd.html\?a=!g;
        $url =~ s!ref=nosim/!!g;
        $url =~ s!ref=nosim!!g;
        $url =~ s!/$!!g;
        $url =~ s!/([^/]*-22)!&amp;uid=NULLGWDOCOMO&amp;url=/gp/aw/d.html&amp;lc=msn&amp;at=$1!;
        $url .= '&amp;dl=1';
        $lnkstr = $mt4ilinkstr;
    } elsif ($url =~ m!.*http://www.amazon.co.jp/gp/product/.*!g) {
        # 新 Amazon リンクなら携帯対応 URL へ変換
        # 個別商品リンクのテキストのみ
        $url =~ s!(http://www.amazon.co.jp/gp/)product/(.*)\?ie=(.*)&tag=(.*)&linkCode.*!$1aw/rd.html?ie=$3&dl=1&uid=NULLGWDOCOMO&a=$2&at=$4&url=%2Fgp%2Faw%2Fd\.html!g;
    } elsif ($url =~ m/.*http:\/\/www.amazon.co.jp\/gp\/redirect.html.*/g) {
        # 新 Amazon リンクなら携帯対応 URL へ変換
        # テキストリンク | 特定のページ
        $url =~ s!(http://www.amazon.co.jp/gp/).*product/(.*)\?ie=(.*)&tag=(.*)&linkCode.*!$1aw/rd.html?ie=$3&dl=1&uid=NULLGWDOCOMO&a=$2&at=$4&url=%2Fgp%2Faw%2Fd\.html!g;
    } elsif ($url =~ m/.*http:\/\/www.amazlet.com\/browse\/ASIN\/.*/g) {
        # Amazletへのリンクなら、Amazonのi-mode対応へ変換
        $url =~ s!www.amazlet.com/browse/ASIN/!www.amazon.co.jp/gp/aw/rd.html?a=!g;
        $url =~ s!/ref=nosim/!!g;
        $url =~ s!/$!!g;
        $url =~ s!/([^/]*-22)!&amp;uid=NULLGWDOCOMO&amp;url=/gp/aw/d.html&amp;lc=msn&amp;at=$1!;
        $url .= '&amp;dl=1';
        $lnkstr = $mt4ilinkstr;
    } else {
        # リンク先を取得
        my $mt4ilink = MT4i::Func::get_mt4ilink($url);
        
        if ($mt4ilink) {
            $url = $mt4ilink;
            $lnkstr = $mt4ilinkstr;
        } else {
            if ($cfg{MobileGW} eq '1') {              # 通勤ブラウザ
                # 'http://'を削除
                $url =~ s!http://!!g;
                # URLを生成
                my $chtmltransurl = 'http://www.sjk.co.jp/c/w.exe?y=';
                $url = $chtmltransurl . $url;
            } elsif ($cfg{MobileGW} eq '2') {           # Google mobile Gateway
                # "/"→"%2F"、"?"→"%3F"、"+"→"%2B"
                $url =~ s/\//\%2F/g;
                $url =~ s/\?/\%3F/g;
                $url =~ s/\+/\%2B/g;
                # URLを生成
                my $chtmltransurl = 'http://www.google.co.jp/gwt/n?u=';
                $url = $chtmltransurl . $url;
            }
        }
    }
    return ($lnkstr,$url);
}

########################################
# Sub Htmlout - HTMLの出力
########################################

sub htmlout {
    # blog_nameから改行を削除
    my $hd_blog_name = $blog_name;
    $hd_blog_name =~ s!<br>!!ig; 
    $hd_blog_name =~ s!<br />!!ig; 
    
    # HTMLヘッダ/フッタ定義
    $data = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD Compact HTML 1.0 Draft//EN\"><html><head><meta name=\"CHTML\" HTTP-EQUIV=\"content-type\" CONTENT=\"text/html; charset=Shift_JIS\"><meta http-equiv=\"Pragma\" content=\"no-cache\"><meta http-equiv=\"Cache-Control\" content=\"no-cache\"><meta http-equiv=\"Cache-Control\" content=\"max-age=0\"><title>$hd_blog_name mobile ver.</title></head><body bgcolor=\"$cfg{BgColor}\" text=\"$cfg{TxtColor}\" link=\"$cfg{LnkColor}\" alink=\"$cfg{AlnkColor}\" vlink=\"$cfg{VlnkColor}\">" . $data;
    if (exists $cfg{AdmNM}) {
        $data .= "<p><center>管理人:";
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
    # 管理者モードではMT4i公式ページへのアンカーを表示しない
    if ($admin_mode eq 'yes') {
        $data .= "MT4i v$version";
    } else {
        $data .= "<a href=\"http://hazama.nu/pukiwiki/?MT4i\">MT4i v$version</a>";
    }
    $data .= "</center></p></body></html>";
    
    # 表示文字列をShift_JISに変換
    if ($ecd == 1) {
        $data = encode("shiftjis",decode("euc-jp",$data));
    } else {
        $data = Jcode->new($data, 'euc')->sjis;
    }
    
    # 表示
    binmode(STDOUT);
    print "Content-type: text/html; charset=Shift_JIS\n";
    print "Content-Length: ",length($data),"\n\n";
    print $data;
}

########################################
# Sub Errorout - エラーの出力
########################################

sub errorout {
    # HTMLヘッダ/フッタ定義
    $data = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD Compact HTML 1.0 Draft//EN\"><html><head><meta name=\"CHTML\" HTTP-EQUIV=\"content-type\" CONTENT=\"text/html; charset=Shift_JIS\"><title>Error</title></head><body>" . $data . "</body></html>";
    
    # 表示文字列をShift_JISに変換
    if ($ecd == 1) {
        $data = encode("shiftjis",decode("euc-jp",$data));
    } else {
        $data = Jcode->new($data, 'euc')->sjis;
    }
    
    # 表示
    binmode(STDOUT);
    print "Content-type: text/html; charset=Shift_JIS\n";
    print "Content-Length: ",length($data),"\n\n";
    print $data;
}

##############################################################
# Sub conv_datetime - YYYYMMDDhhmmssを MM/DD hh:mm に変換
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
# Sub Check_Category - エントリのプライマリカテゴリラベルを取得
#  プライマリカテゴリが非表示設定されている場合は最初に出てきた
#  サブカテゴリのラベルを取得
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
# Sub Conv_Euc2icode - EUC-JP→MT使用コード変換
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
# Sub Get_CatList - セレクタ用カテゴリリストの取得
##################################################
sub get_catlist {
    my @categories;

    require MT::Category;
    my @cats = MT::Category->top_level_categories($cfg{Blog_ID});

    # ソート
    my @s_cats = &sort_cat(@cats);

    # サブカテゴリの取得
    foreach my $category (@s_cats) {
        my @c_cats = &get_subcatlist($category, 0);
        foreach my $c_category (@c_cats) {
            push @categories, $c_category;
        }
    }
    return @categories;
}

##################################################
# Sub Get_SubCatList - セレクタ用サブカテゴリリストの取得
##################################################
sub get_subcatlist {
    my $category = shift;
    my $hierarchy = shift;
    
    # 管理者モードでない場合には非表示カテゴリを処理する
    # 親カテゴリが非表示なら子カテゴリも表示しない
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
    # カテゴリの列挙
    my %terms = (blog_id => $cfg{Blog_ID});
    # 管理者モードでなければステータスが'公開'のエントリのみカウント
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
        # カテゴリ名ぶった切り
        if ($cfg{LenCutCat} > 0) {
            if (MT4i::Func::lenb_euc($label) > $cfg{LenCutCat}) {
                $label = MT4i::Func::midb_euc($label, 0, $cfg{LenCutCat});
            }
        }
        $label = $blank . $label;
    } else {
        $label = &conv_euc_z2h($category->{column_values}->{label});
        # カテゴリ名ぶった切り
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
        # ソート
        my @s_cats = &sort_cat(@cats);

        # サブカテゴリの取得
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
# Sub Sort_Cat - セレクタ用カテゴリリストのソート
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
# Sub Get_NonDispCats - 非表示カテゴリリストの取得
##################################################
sub get_nondispcats {
    my @nondispcats = split(",", $cfg{NonDispCat});
    my @nonsubdispcats;
    foreach my $nondispcatid (@nondispcats) {
        # IDからカテゴリオブジェクトを取得
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
