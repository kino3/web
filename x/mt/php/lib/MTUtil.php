<?php
# Copyright 2001-2005 Six Apart. This code cannot be redistributed without
# permission from www.sixapart.com.  For more information, consult your
# Movable Type license.
#
# $Id: MTUtil.php 16484 2005-08-22 02:43:44Z bchoate $

function start_end_ts($ts) {
    if ($ts) {
        if (strlen($ts) == 4) {
            $ts_start = $ts . '0101';
            $ts_end = $ts . '1231';
        } elseif (strlen($ts) == 6) {
            $ts_start = $ts . '01';
            $ts_end = $ts . sprintf("%02d", days_in(substr($ts, 4, 2), substr($ts, 0, 4)));
        } else {
            $ts_start = $ts;
            $ts_end = $ts;
        }
    }
    return array($ts_start . '000000', $ts_end . '235959');
}

function start_end_month($ts) {
    $y = substr($ts, 0, 4);
    $mo = substr($ts, 4, 2);
    $start = sprintf("%04d%02d01000000", $y, $mo);
    $end = sprintf("%04d%02d%02d235959", $y, $mo, days_in($mo, $y));
    return array($start, $end);
}

function days_in($m, $y) {
    return date('t', mktime(0, 0, 0, $m, 1, $y));
}

function start_end_day($ts) {
    $day = substr($ts, 0, 8);
    return array($day . "000000", $day . "235959");
}

function start_end_year($ts) {
    $year = substr($ts, 0, 4);
    return array($year . "0101000000", $year . "1231235959");
}

function start_end_week($ts) {
    $y = substr($ts, 0, 4);
    $mo = substr($ts, 4, 2);
    $d = substr($ts, 6, 2);
    $h = substr($ts, 8, 2);
    $s = substr($ts, 10, 2);
    $wday = wday_from_ts($y, $mo, $d);
    list($sd, $sm, $sy) = array($d - $wday, $mo, $y);
    if ($sd < 1) {
        $sm--;
        if ($sm < 1) {
            $sm = 12; $sy--;
        }
        $sd += days_in($sm, $sy);
    }
    $start = sprintf("%04d%02d%02d%s", $sy, $sm, $sd, "000000");
    list($ed, $em, $ey) = array($d + 6 - $wday, $mo, $y);
    if ($ed > days_in($em, $ey)) {
        $ed -= days_in($em, $ey);
        $em++;
        if ($em > 12) {
            $em = 1; $ey++;
        }
    }
    $end = sprintf("%04d%02d%02d%s", $ey, $em, $ed, "235959");
    return array($start, $end);
}

global $In_Year;
$In_Year = array(
    array( 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365 ),
    array( 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366 ),
);
function week2ymd($y, $week) {
    $jan_one_dow_m1 = (ymd2rd($y, 1, 1) + 6) % 7;

    if ($jan_one_dow_m1 < 4) $week--;
    $day_of_year = $week * 7 - $jan_one_dow_m1 + 1;
    $leap_year = is_leap_year($y);
    if ($day_of_year < 1) {
        $y--;
        $day_of_year = ($leap_year ? 366 : 365) + $day_of_year;
    }
    if ($leap_year) {
        $ref = array(0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335);
    } else {
        $ref = array(0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334);
    }
    $m = 0;
    for ($i = count($ref); $i > 0; $i--) {
        if ($day_of_year > $ref[$i-1]) {
            $m = $i;
            break;
        }
    }
    return array($y, $m, $day_of_year - $ref[$m-1]);
}

function is_leap_year($y) {
    return (!($y % 4) && ($y % 100)) || !($y % 400) ? true : false;
}

function ymd2rd($y,$m,$d) {
    # make month in range 3..14 (treat Jan & Feb as months 13..14 of
    # prev year)
    if ( $m <= 2 ) {
        $adj = (int)(( 14 - $m ) / 12);
        $y -= $adj;
        $m += 12 * $adj;
    }
    elseif ( $m > 14 )
    {
        $adj = (int)(( $m - 3 ) / 12);
        $y += $adj;
        $m -= 12 * $adj;
    }

    # make year positive (oh, for a use integer 'sane_div'!)
    if ( $y < 0 )
    {
        $adj = (int)(( 399 - $y ) / 400);
        $d -= 146097 * $adj; 
        $y += 400 * $adj;
    }

    # add: day of month, days of previous 0-11 month period that began
    # w/March, days of previous 0-399 year period that began w/March
    # of a 400-multiple year), days of any 400-year periods before
    # that, and 306 days to adjust from Mar 1, year 0-relative to Jan
    # 1, year 1-relative (whew)
    $d += (int)(( $m * 367 - 1094 ) / 12) + (int)((($y % 100) * 1461) / 4) +
          ( (int)($y / 100) * 36524 + (int)($y / 400) ) - 306;
    return $d;
}

function wday_from_ts($y, $m, $d) {
    global $In_Year;
    $leap = $y % 4 == 0 && ($y % 100 != 0 || $y % 400 == 0) ? 1 : 0;
    $y--;

    ## Copied from Date::Calc.
    $days = $y * 365;
    $days += $y >>= 2;
    $days -= intval($y /= 25);
    $days += $y >> 2;
    $days += $In_Year[$leap][$m-1] + $d;
    return $days % 7;
}

function yday_from_ts($y, $m, $d) {
    global $In_Year;
    $leap = $y % 4 == 0 && ($y % 100 != 0 || $y % 400 == 0) ? 1 : 0;
    return $In_Year[$leap][$m-1] + $d;
}

function substr_wref($str, $start, $length) {
    if (preg_match_all('/(&[^;]*;|.)/', $str, $character_entities)) {
        return implode('', array_slice($character_entities[0], $start, $length));
    } else {
        return '';
    }
}

function format_ts($format, $ts, $blog, $lang = null) {
    global $Languages;
    if (!isset($lang) || empty($lang)) { 
        global $mt;
        $lang = ($blog && $blog['blog_language'] ? $blog['blog_language'] : 
                     $mt->config['DefaultLanguage']);
    }
    if ($lang == 'jp') {
        $lang = 'ja';
    }
    if (!isset($format) || empty($format)) {
        if (count($Languages[$lang]) >= 4)
            $format = $Languages[$lang][3];
        $format or $format = "%B %e, %Y %I:%M %p";
    }
    global $_format_ts_cache;
    if (!isset($_format_ts_cache)) {
        $_format_ts_cache = array();
    }   
    if (isset($_format_ts_cache[$ts.$lang])) {
        $f = $_format_ts_cache[$ts.$lang];
    } else {
        $L = $Languages[$lang];
        $tsa = array(substr($ts, 0, 4), substr($ts, 4, 2), substr($ts, 6, 2),
                     substr($ts, 8, 2), substr($ts, 10, 2), substr($ts, 12, 2));
        list($f['Y'], $f['m'], $f['d'], $f['H'], $f['M'], $f['S']) = $tsa;
        $f['w'] = wday_from_ts($tsa[0],$tsa[1],$tsa[2]);
        $f['j'] = yday_from_ts($tsa[0],$tsa[1],$tsa[2]);
        $f['y'] = substr($f['Y'], 2);
        $f['b'] = substr_wref($L[1][$f['m']-1], 0, 3);
        $f['B'] = $L[1][$f['m']-1];
        if ($lang == 'ja') {
            $f['a'] = substr($L[0][$f['w']], 0, 8);
        } else {
            $f['a'] = substr_wref($L[0][$f['w']], 0, 3);
        }
        $f['A'] = $L[0][$f['w']];
        $f['e'] = $f['d'];
        $f['e'] = preg_replace('!^0!', ' ', $f['e']);
        $f['I'] = $f['H'];
        if ($f['I'] > 12) {
            $f['I'] -= 12;
            $f['p'] = $L[2][1];
        } elseif ($f['I'] == 0) {
            $f['I'] = 12;
            $f['p'] = $L[2][0];
        } elseif ($f['I'] == 12) {
            $f['p'] = $L[2][1];
        } else {
            $f['p'] = $L[2][0];
        }
        $f['I'] = sprintf("%02d", $f['I']);
        $f['k'] = $f['H'];
        $f['k'] = preg_replace('!^0!', ' ', $f['k']);
        $f['l'] = $f['I'];
        $f['l'] = preg_replace('!^0!', ' ', $f['l']);
        $f['j'] = sprintf("%03d", $f['j']);
        $f['Z'] = '';
        $_format_ts_cache[$ts . $lang] = $f;
    }
    $date_format = null;
    if (count($Languages[$lang]) >= 5)
        $date_format = $Languages[$lang][4];
    $date_format or $date_format = "%B %d, %Y";
    $time_format = null;
    if (count($Languages[$lang]) >= 6)
        $time_format = $Languages[$lang][5];
    $time_format or $time_format = "%I:%M %p";
    $format = preg_replace('!%x!', $date_format, $format);
    $format = preg_replace('!%X!', $time_format, $format);
    ## This is a dreadful hack. I can't think of a good format specifier
    ## for "%B %Y" (which is used for monthly archives, for example) so
    ## I'll just hardcode this, for Japanese dates.
    if ($lang == 'ja') {
        if (count($Languages[$lang]) >= 7)
            $format = preg_replace('!%B %Y!', $Languages[$lang][6], $format);
    }
    if (isset($format)) {
        $format = preg_replace('!%(\w)!e', '\$f[\'\1\']', $format);
    }
    return $format;
}

function dirify($s, $sep = '_') {
    global $mt;
    $charset = $mt->config['PublishCharset'];
    if (preg_match('/utf-?8/i', $charset)) {
        return utf8_dirify($s, $sep);
    } else {
        return iso_dirify($s, $sep);
    }
}

function utf8_dirify($s, $sep = '_') {
    if ($sep == '1') $sep = '_';
    $s = xliterate_utf8($s);  ## convert high-ASCII chars to 7bit.
    $s = strtolower($s);                   ## lower-case.
    $s = strip_tags($s);          ## remove HTML tags.
    $s = preg_replace('!&[^;\s]+;!', '', $s); ## remove HTML entities.
    $s = preg_replace('![^\w\s]!', '', $s);   ## remove non-word/space chars.
    $s = preg_replace('/ +/',$sep,$s);         ## change space chars to underscores.
    return($s);
}

global $Utf8_ASCII;
$Utf8_ASCII = array(
    "\xc3\x80" => 'A',    # A`
    "\xc3\xa0" => 'a',    # a`
    "\xc3\x81" => 'A',    # A'
    "\xc3\xa1" => 'a',    # a'
    "\xc3\x82" => 'A',    # A^
    "\xc3\xa2" => 'a',    # a^
    "\xc3\x84" => 'Ae',   # A:
    "\xc3\xa4" => 'ae',   # a:
    "\xc3\x83" => 'A',    # A~
    "\xc3\xa3" => 'a',    # a~
    "\xc3\x88" => 'E',    # E`
    "\xc3\xa8" => 'e',    # e`
    "\xc3\x89" => 'E',    # E'
    "\xc3\xa9" => 'e',    # e'
    "\xc3\x8a" => 'E',    # E^
    "\xc3\xaa" => 'e',    # e^
    "\xc3\x8b" => 'Ee',   # E:
    "\xc3\xab" => 'ee',   # e:
    "\xc3\x8c" => 'I',    # I`
    "\xc3\xac" => 'i',    # i`
    "\xc3\x8d" => 'I',    # I'
    "\xc3\xad" => 'i',    # i'
    "\xc3\x8e" => 'I',    # I^
    "\xc3\xae" => 'i',    # i^
    "\xc3\x8f" => 'Ie',   # I:
    "\xc3\xaf" => 'ie',   # i:
    "\xc3\x92" => 'O',    # O`
    "\xc3\xb2" => 'o',    # o`
    "\xc3\x93" => 'O',    # O'
    "\xc3\xb3" => 'o',    # o'
    "\xc3\x94" => 'O',    # O^
    "\xc3\xb4" => 'o',    # o^
    "\xc3\x96" => 'Oe',   # O:
    "\xc3\xb6" => 'oe',   # o:
    "\xc3\x95" => 'O',    # O~
    "\xc3\xb5" => 'o',    # o~
    "\xc3\x98" => 'Oe',   # O/
    "\xc3\xb8" => 'oe',   # o/
    "\xc3\x99" => 'U',    # U`
    "\xc3\xb9" => 'u',    # u`
    "\xc3\x9a" => 'U',    # U'
    "\xc3\xba" => 'u',    # u'
    "\xc3\x9b" => 'U',    # U^
    "\xc3\xbb" => 'u',    # u^
    "\xc3\x9c" => 'Ue',   # U:
    "\xc3\xbc" => 'ue',   # u:
    "\xc3\x87" => 'C',    # ,C
    "\xc3\xa7" => 'c',    # ,c
    "\xc3\x91" => 'N',    # N~
    "\xc3\xb1" => 'n',    # n~
    "\xc3\x9f" => 'ss',   # double-s
);
function xliterate_utf8($s) {
    global $Utf8_ASCII;
    return strtr($s, $Utf8_ASCII);
}

function iso_dirify($s, $sep = '_') {
    if ($sep == '1') $sep = '_';
    $s = convert_high_ascii($s);  ## convert high-ASCII chars to 7bit.
    $s = strtolower($s);                   ## lower-case.
    $s = strip_tags($s);          ## remove HTML tags.
    $s = preg_replace('!&[^;\s]+;!', '', $s); ## remove HTML entities.
    $s = preg_replace('![^\w\s]!', '', $s);   ## remove non-word/space chars.
    $s = preg_replace('/ +/',$sep,$s);         ## change space chars to underscores.
    return($s);
}

global $Latin1_ASCII;
$Latin1_ASCII = array(
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
function convert_high_ascii($s) {
    global $Latin1_ASCII;
    return strtr($s, $Latin1_ASCII);
}

global $Languages;
$Languages = array(
    'en' => array(
            array('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'),
            array('January','February','March','April','May','June',
                  'July','August','September','October','November','December'),
            array('AM','PM'),
          ),

    'en-us' => array(
            array('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'),
            array('January','February','March','April','May','June',
                  'July','August','September','October','November','December'),
            array('AM','PM'),
          ),

    'en_us' => array(
            array('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'),
            array('January','February','March','April','May','June',
                  'July','August','September','October','November','December'),
            array('AM','PM'),
          ),

    'fr' => array(
            array('dimanche','lundi','mardi','mercredi','jeudi','vendredi','samedi' ),
            array('janvier', "f&#xe9;vrier", 'mars', 'avril', 'mai', 'juin',
               'juillet', "ao&#xfb;t", 'septembre', 'octobre', 'novembre',
               "d&#xe9;cembre"),
            array('AM','PM'),
          ),

    'es' => array(
            array('Domingo', 'Lunes', 'Martes', "Mi&#xe9;rcoles", 'Jueves',
               'Viernes', "S&#xe1;bado"),
            array('Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto',
                  'Septiembre','Octubre','Noviembre','Diciembre'),
            array('AM','PM'),
          ),

    'pt' => array(
            array('domingo', 'segunda-feira', "ter&#xe7;a-feira", 'quarta-feira',
               'quinta-feira', 'sexta-feira', "s&#xe1;bado"),
            array('janeiro', 'fevereiro', "mar&#xe7;o", 'abril', 'maio', 'junho',
               'julho', 'agosto', 'setembro', 'outubro', 'novembro',
               'dezembro' ),
            array('AM','PM'),
          ),

    'nl' => array(
            array('zondag','maandag','dinsdag','woensdag','donderdag','vrijdag',
                  'zaterdag'),
            array('januari','februari','maart','april','mei','juni','juli','augustus',
                  'september','oktober','november','december'),
            array('am','pm'),
             "%d %B %Y %H:%M",
             "%d %B %Y"
          ),

    'dk' => array(
            array("s&#xf8;ndag", 'mandag', 'tirsdag', 'onsdag', 'torsdag',
               'fredag', "l&#xf8;rdag"),
            array('januar','februar','marts','april','maj','juni','juli','august',
                  'september','oktober','november','december'),
            array('am','pm'),
            "%d.%m.%Y %H:%M",
            "%d.%m.%Y",
            "%H:%M",
          ),

    'se' => array(
            array("s&#xf6;ndag", "m&#xe5;ndag", 'tisdag', 'onsdag', 'torsdag',
               'fredag', "l&#xf6;rdag"),
            array('januari','februari','mars','april','maj','juni','juli','augusti',
                  'september','oktober','november','december'),
            array('FM','EM'),
          ),

    'no' => array(
            array("S&#xf8;ndag", "Mandag", 'Tirsdag', 'Onsdag', 'Torsdag',
               'Fredag', "L&#xf8;rdag"),
            array('Januar','Februar','Mars','April','Mai','Juni','Juli','August',
                  'September','Oktober','November','Desember'),
            array('FM','EM'),
          ),

    'de' => array(
            array('Sonntag','Montag','Dienstag','Mittwoch','Donnerstag','Freitag',
                  'Samstag'),
            array('Januar', 'Februar', "M&#xe4;rz", 'April', 'Mai', 'Juni',
               'Juli', 'August', 'September', 'Oktober', 'November',
               'Dezember'),
            array('FM','EM'),
            "%d.%m.%y %H:%M",
            "%d.%m.%y",
            "%H:%M",
          ),

    'it' => array(
            array('Domenica', "Luned&#xec;", "Marted&#xec;", "Mercoled&#xec;",
               "Gioved&#xec;", "Venerd&#xec;", 'Sabato'),
            array('Gennaio','Febbraio','Marzo','Aprile','Maggio','Giugno','Luglio',
                  'Agosto','Settembre','Ottobre','Novembre','Dicembre'),
            array('AM','PM'),
            "%d.%m.%y %H:%M",
            "%d.%m.%y",
            "%H:%M",
          ),

    'pl' => array(
            array('niedziela', "poniedzia&#322;ek", 'wtorek', "&#347;roda",
               'czwartek', "pi&#261;tek", 'sobota'),
            array('stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca',
               'lipca', 'sierpnia', "wrze&#347;nia", "pa&#378;dziernika",
               'listopada', 'grudnia'),
            array('AM','PM'),
            "%e %B %Y %k:%M",
            "%e %B %Y",
            "%k:%M",
          ),
            
    'fi' => array(
            array('sunnuntai','maanantai','tiistai','keskiviikko','torstai','perjantai',
                  'lauantai'),
            array('tammikuu', 'helmikuu', 'maaliskuu', 'huhtikuu', 'toukokuu',
               "kes&#xe4;kuu", "hein&#xe4;kuu", 'elokuu', 'syyskuu', 'lokakuu',
               'marraskuu', 'joulukuu'),
            array('AM','PM'),
            "%d.%m.%y %H:%M",
          ),
            
    'is' => array(
            array('Sunnudagur', "M&#xe1;nudagur", "&#xde;ri&#xf0;judagur",
               "Mi&#xf0;vikudagur", 'Fimmtudagur', "F&#xf6;studagur",
               'Laugardagur'),
            array("jan&#xfa;ar", "febr&#xfa;ar", 'mars', "apr&#xed;l", "ma&#xed;",
               "j&#xfa;n&#xed;", "j&#xfa;l&#xed;", "&#xe1;g&#xfa;st", 'september',             
               "okt&#xf3;ber", "n&#xf3;vember", 'desember'),
            array('FH','EH'),
            "%d.%m.%y %H:%M",
          ),
            
    'si' => array(
            array('nedelja', 'ponedeljek', 'torek', 'sreda', "&#xe3;etrtek",
               'petek', 'sobota'),
            array('januar','februar','marec','april','maj','junij','julij','avgust',
                  'september','oktober','november','december'),
            array('AM','PM'),
            "%d.%m.%y %H:%M",
          ),
            
    'cz' => array(
            array('Ned&#283;le', 'Pond&#283;l&#237;', '&#218;ter&#253;',
               'St&#345;eda', '&#268;tvrtek', 'P&#225;tek', 'Sobota'),
            array('Leden', '&#218;nor', 'B&#345;ezen', 'Duben', 'Kv&#283;ten',
               '&#268;erven', '&#268;ervenec', 'Srpen', 'Z&#225;&#345;&#237;',
               '&#216;&#237;jen', 'Listopad', 'Prosinec'),
            array('AM','PM'),
            "%e. %B %Y %k:%M",
            "%e. %B %Y",
            "%k:%M",
          ),
            
    'sk' => array(
            array('nede&#318;a', 'pondelok', 'utorok', 'streda',
               '&#353;tvrtok', 'piatok', 'sobota'),
            array('janu&#225;r', 'febru&#225;r', 'marec', 'apr&#237;l',
               'm&#225;j', 'j&#250;n', 'j&#250;l', 'august', 'september',
               'okt&#243;ber', 'november', 'december'),
            array('AM','PM'),
            "%e. %B %Y %k:%M",
            "%e. %B %Y",
            "%k:%M",
          ),

    'jp' => array(
            array('&#26085;&#26332;&#26085;', '&#26376;&#26332;&#26085;',
              '&#28779;&#26332;&#26085;', '&#27700;&#26332;&#26085;',
              '&#26408;&#26332;&#26085;', '&#37329;&#26332;&#26085;',
              '&#22303;&#26332;&#26085;'),
            array('1','2','3','4','5','6','7','8','9','10','11','12'),
            array('AM','PM'),
            "%Y&#24180;%m&#26376;%d&#26085; %H:%M",
            "%Y&#24180;%m&#26376;%d&#26085;",
            "%H:%M",
            "%Y&#24180;%m&#26376;",
          ),

    'ja' => array(
            array('&#26085;&#26332;&#26085;', '&#26376;&#26332;&#26085;',
              '&#28779;&#26332;&#26085;', '&#27700;&#26332;&#26085;',
              '&#26408;&#26332;&#26085;', '&#37329;&#26332;&#26085;',
              '&#22303;&#26332;&#26085;'),
            array('1','2','3','4','5','6','7','8','9','10','11','12'),
            array('AM','PM'),
            "%Y&#24180;%m&#26376;%d&#26085; %H:%M",
            "%Y&#24180;%m&#26376;%d&#26085;",
            "%H:%M",
            "%Y&#24180;%m&#26376;",
          ),

    'et' => array(
            array('ip&uuml;hap&auml;ev','esmasp&auml;ev','teisip&auml;ev',
                  'kolmap&auml;ev','neljap&auml;ev','reede','laup&auml;ev'),
            array('jaanuar', 'veebruar', 'm&auml;rts', 'aprill', 'mai',
               'juuni', 'juuli', 'august', 'september', 'oktoober',
              'november', 'detsember'),
            array('AM','PM'),
            "%m.%d.%y %H:%M",
            "%e. %B %Y",
            "%H:%M",
          ),
);

global $_encode_xml_Map;
$_encode_xml_Map = array('&' => '&amp;', '"' => '&quot;',
                         '<' => '&lt;', '>' => '&gt;',
                         '\'' => '&apos;');

function encode_xml($str, $nocdata = 0) {
    global $mt, $_encode_xml_Map;
    $nocdata or (isset($mt->config['NoCDATA']) and $nocdata = $mt->config['NoCDATA']);
    if ((!$nocdata) && (preg_match('/
        <[^>]+>  ## HTML markup
        |        ## or
        &(?:(?!(\#([0-9]+)|\#x([0-9a-fA-F]+))).*?);
                 ## something that looks like an HTML entity.
        /x', $str))) {
        ## If ]]> exists in the string, encode the > to &gt;.
        $str = preg_replace('/]]>/', ']]&gt;', $str);
        $str = '<![CDATA[' . $str . ']]>';
    } else {
        $str = strtr($str, $_encode_xml_Map);
    }
    return $str;
}

function decode_xml($str) {
    if (preg_match('/<!\[CDATA\[(.*?)]]>/', $str)) {
        $str = preg_replace('/<!\[CDATA\[(.*?)]]>/', '\1', $str);
        ## Decode encoded ]]&gt;
        $str = preg_replace('/]]&(gt|#62);/', ']]>', $str);
    } else {
        global $_encode_xml_Map;
        $str = strtr($str, array_flip($_encode_xml_Map));
    }
    return $str;
}

function encode_js($str) {
    if (!isset($str)) return '';
    $str = preg_replace('!\\!', '\\\\', $str);
    $str = preg_replace('!\'!', '\\\'', $str);
    $str = preg_replace('!"!', '\\"', $str);
    $str = preg_replace('!\n!', '\\n', $str);
    $str = preg_replace('!\f!', '\\f', $str);
    $str = preg_replace('!\r!', '\\r', $str);
    $str = preg_replace('!\t!', '\\t', $str);
    return $str;
}

function gmtime($ts = null) {
    if (!isset($ts)) {
        $ts = time();
    }
    $offset = date('Z', $ts);
    $ts -= $offset;
    $tsa = localtime($ts);
    $tsa[8] = 0;
    return $tsa;
}

function offset_time_list($ts, $blog = null, $dir = null) {
    return gmtime(offset_time($ts, $blog, $dir));
}

function strip_hyphen($s) {
    return preg_replace('/-+/', '-', $s);
}

function first_n_words($text, $n) {
    $text = strip_tags($text);
    $words = preg_split('/\s+/', $text);
    $max = count($words) > $n ? $n : count($words);
    return join(' ', array_slice($words, 0, $max));
}

function html_text_transform($str = '') {
    $paras = preg_split('/\r?\n\r?\n/', $str);
    if ($str == '') {
        return '';
    }
    foreach ($paras as $k => $p) {
        if (!preg_match('/^<\/?(?:h1|h2|h3|h4|h5|h6|table|ol|dl|ul|menu|dir|p|pre|center|form|select|fieldset|blockquote|address|div|hr)/', $p)) {
            $p = preg_replace('/\r?\n/', "<br />\n", $p);
            $p = "<p>$p</p>";
            $paras[$k] = $p;
        }
    }
    return implode("\n\n", $paras);
}

function encode_html($str, $quote_style = ENT_COMPAT) {
    if (!isset($str)) return '';
    $trans_table = get_html_translation_table(HTML_SPECIALCHARS, $quote_style);
    if( $trans_table["'"] != '&#039;' ) { # some versions of PHP match single quotes to &#39;
        $trans_table["'"] = '&#039;';
    }
    return (strtr($str, $trans_table));
}

function decode_html($str, $quote_style = ENT_COMPAT) {
    if (!isset($str)) return '';
    $trans_table = get_html_translation_table(HTML_SPECIALCHARS, $quote_style);
    if( $trans_table["'"] != '&#039;' ) { # some versions of PHP match single quotes to &#39;
        $trans_table["'"] = '&#039;';
    }
    return (strtr($str, array_flip($trans_table)));
}

function get_category_context(&$ctx) {
    # Get our hands on the category for the current context
    # Either in MTCategories, a Category Archive Template
    # Or the category for the current entry
    $cat = $ctx->stash('category') or
           $ctx->stash('archive_category');

    if (!isset($cat)) {
        # No category found so far, test the entry
        if ($ctx->stash('entry')) {
            $entry = $ctx->stash('entry');
            $cat = $ctx->mt->db->fetch_category($entry['placement_category_id']);
  
            # Return empty string if entry has no category
            # as the tag has been used in the correct context
            # but there is no category to work with
            if (!isset($cat)) {
                return null;
            }
        } else {
            $tag = $ctx->this_tag();
            return $ctx->error("MT$tag must be used in a category context");
        }
    }
    return $cat;
}

function munge_comment($text, $blog) {
    if (!$blog['blog_allow_comment_html']) {
        $text = strip_tags($text);
        if ($blog['blog_autolink_urls']) {
            $text = preg_replace('!(http://\S+)!', '<a href="$1">$1</a>', $text);
        }
    }
    return $text;
}

function length_text($text) {
    if (!extension_loaded('mbstring')) {
        $len = strlen($text);
    } else {
        $len = mb_strlen($text);
    }
    return $len;
}

function substr_text($text, $startpos, $length) {
    if (!extension_loaded('mbstring')) {
        $text = substr($text, $startpos, $length);
    } else {
        $text = mb_substr($text, $startpos, $length);
    }
    return $text;
}

function first_n_text($text, $n) {
    $text = strip_tags($text);
    $text = preg_replace('/\r?\n/', " ", $text);
    return substr_text($text, 0, $n);
}
?>
