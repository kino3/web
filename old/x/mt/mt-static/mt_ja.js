/*
Copyright 2001-2005 Six Apart. This code cannot be redistributed without
permission from www.sixapart.com.  For more information, consult your
Movable Type license.

$Id: mt.js 16607 2005-08-24 06:22:16Z jallen $
*/

var ScriptURI;
var ScriptBaseURI;
var StaticURI;
var HelpBaseURI;

if ((!(navigator.appVersion.indexOf('MSIE') != -1) &&
      (parseInt(navigator.appVersion)==4))) {
    document.write("<style type=\"text/css\">");
    document.write("body { margin-top: -8px; margin-left: -8px; }"); 
    document.write("</style>");
}

var origWidth, origHeight;
if ((navigator.appName == 'Netscape') &&
    (parseInt(navigator.appVersion) == 4)) {
    origWidth = innerWidth;
    origHeight = innerHeight;
    window.onresize = restore;
}

function restore () {
    if (innerWidth != origWidth || innerHeight != origHeight)
        location.reload();
}

function doRebuild (blogID, otherParams) {
    window.open(ScriptURI + '?__mode=rebuild_confirm&blog_id=' + blogID + '&' + otherParams, 'rebuild', 'width=400,height=250,resizable=yes');
}

function openManual (section, page) {
    window.open(HelpBaseURI + 'g_contextsensitive_help/' + section + '/' + page + '.html' , '_blank', 
'width=800,height=600,scrollbars=yes,status=yes,resizable=yes,toolbar=yes,location=yes,menubar=yes');
    return false;
}

function gatherMarked (f, nameRestrict) {
    var url = '';
    var e = f.id;
    if (!e) return;
    if (e.value && e.checked)
        url += '&id=' + e.value;
    else
	if (nameRestrict) {
	    for (i=0; i<e.length; i++)
        	if (e[i].checked && (e[i].name == nameRestrict))
                    url += '&id=' + e[i].value;
	} else {
	    for (i=0; i<e.length; i++)
        	if (e[i].checked)
                    url += '&id=' + e[i].value;
	}
   return url;
}

function countMarked (f, nameRestrict) {
    var count = 0;
    var e = f.id;
    if (!e) return 0;
    if (e.type && e.type == 'hidden') return 1;
    if (e.value && e.checked)
        count++;
    else
	if (nameRestrict) {
	    for (i=0; i<e.length; i++)
        	if (e[i].checked && (e[i].name == nameRestrict))
                    count++;
	} else {
	    for (i=0; i<e.length; i++)
        	if (e[i].checked)
                    count++;
	}
   return count;
}

function doRemoveItems (f, singular, plural, nameRestrict, args) {
    var count = countMarked(f, nameRestrict);
    if (!count) {
        alert('\u524a\u9664\u3059\u308b' + plural + '\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002');
        return false;
    }
    if (confirm(count == 1 ? '\u3053\u306e' + singular +'\u3092\u524a\u9664\u3057\u3066\u3044\u3044\u3067\u3059\u304b?' : count + '\u4ef6\u306e' + plural +'\u3092\u524a\u9664\u3057\u3066\u3044\u3044\u3067\u3059\u304b?')) {
        return doForMarkedInThisWindow(f, singular, plural, nameRestrict, 'delete', args, 'to delete');
    }
}

function doForMarkedInThisWindow (f, singular, plural, nameRestrict, 
                                  mode, args, phrase) {
    var count = countMarked(f, nameRestrict);
    if (!count) {
        alert(phrase + '\u3059\u308b' + plural + '\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002');
        return false;
    }
    f.elements["__mode"].value = mode;
    if (args) {
        for (var arg in args)
            f.elements[arg].value = args[arg];
    }
    f.submit();
}

function submitForm(f, mode) {
    if (f.elements["__mode"] && mode) {
        f.elements["__mode"].value = mode;
    }
    f.submit();
}

function doPluginAction(f, plural, phrase) {
    var sel = f['plugin_action_selector'];
    if (sel.length && sel[0].options) sel = sel[0];
    var action = sel.options[sel.selectedIndex].value;
    if (action == '0' || action == '') {
        alert("\u30d7\u30eb\u30c0\u30a6\u30f3\u30fb\u30e1\u30cb\u30e5\u30fc\u304b\u3089\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002");
        return;
    }
    return doForMarkedInThisWindow(f, '', plural, 'id', 'itemset_action', { 'action_name' : action }, phrase);
}

function updatePluginAction(s) {
    var frm = s.form;
    frm.elements['plugin_action_selector'].value = s[s.selectedIndex].value;
    // synchronize top and bottom plugin action selection
    var el = frm[s.name];
    for (var i = 0; i < el.length; i++)
        if (el[i].selectedIndex != s.selectedIndex)
            el[i].selectedIndex = s.selectedIndex;
}

function doItemsAreJunk (f, singular, plural, nameRestrict) {
    doForMarkedInThisWindow(f, singular, plural, nameRestrict,
        'handle_junk', {}, '\u8ff7\u60d1\u30b3\u30e1\u30f3\u30c8/\u30c8\u30e9\u30c3\u30af\u30d0\u30c3\u30af\u3068\u3057\u3066\u8a2d\u5b9a');
}

function doItemsAreNotJunk (f, singular, plural, nameRestrict) {
    doForMarkedInThisWindow(f, singular, plural, nameRestrict,
        'not_junk', {}, '\u8ff7\u60d1\u30b3\u30e1\u30f3\u30c8/\u30c8\u30e9\u30c3\u30af\u30d0\u30c3\u30af\u304b\u3089\u89e3\u9664');
}

function doRemoveItem (f, id, type) {
    var url = ScriptURI;
    url += '?__mode=delete_confirm&_type=' + type + '&id=' + id + '&return_args=' + (f ? escape(f['return_args'].value) : '');
    window.open(url, 'confirm_delete', 'width=370,height=250,scrollbars=yes');
}

function getByID (n) {
    var d = window.document;
    if (d.getElementById)
        return d.getElementById(n);
    else if (d.all)
        return d.all[n];
}

var theForm;
var requestSubmitted = false;
function disableButton (e) {
    if (!requestSubmitted) {
        e.disabled = true;
        theForm = e.form;
        requestSubmitted = true;
        setTimeout('submitIt()', 250);
    } else {
        return false;
    }
}

function submitIt () {
    theForm.submit();
    return false;
}

function checkAndSubmit (f) {
    if (requestSubmitted == true) {
        return false;
    } else {
        requestSubmitted = true;
        f.submit();
        return false;
    }
}

function dirify (str) {
    var s = str.toLowerCase();
    s = s.replace(/&[^;\s]+;/g, '');
    s = s.replace(/[^\w\s]/g, '');
    s = s.replace(/\s+/g, '_');
    return s;
}

var canFormat = 0;
if (document.selection)
    canFormat = 1;
var ua = navigator.userAgent;
if (ua.indexOf('Gecko') >= 0 && ua.indexOf('Safari') < 0)
    canFormat = 1;

function getSelected (e) {
    if (document.selection) {
        e.focus();
        var range = document.selection.createRange();
        return range.text;
    } else {
        var length = e.textLength;
	if (length == undefined) return;
        var start = e.selectionStart;
        var end = e.selectionEnd;
        if (end == 1 || end == 2) end = length;
        return e.value.substring(start, end);
    }
}

function setSelection (e, v) {
    if (document.selection) {
        e.focus();
        var range = document.selection.createRange();
        range.text = v;
    } else {
        var length = e.textLength;
        var start = e.selectionStart;
        var end = e.selectionEnd;
        if (end == 1 || end == 2) end = length;
        e.value = e.value.substring(0, start) + v + e.value.substr(end, length);
        e.selectionStart = start + v.length;
        e.selectionEnd = start + v.length;
    }
    e.focus();
}

function formatStr (e, v) {
    if (!canFormat) return;
    var str = getSelected(e);
    if (!str) return;
    setSelection(e, '<' + v + '>' + str + '</' + v + '>');
    return false;
}

function mtShortCuts(e) {
    e = e || event;
    if (!e || (!e.ctrlKey)) return;
    /* we have to add 64 to keyCode since the user hit a control key */
    var code = (e.keyCode) ? (e.keyCode + 64) :
               ((e.which) ? e.which : 0);
    var ch = String.fromCharCode(code);
    el = e.target || e.srcElement;
    if (el.nodeType == 3) el = el.parentNode; // Safari bug
    if (ch == 'A') insertLink(el, false);
    if (ch == 'B') formatStr(el, 'strong');
    if (ch == 'I') formatStr(el, 'em');
    if (ch == 'U') formatStr(el, 'u');
}

function insertLink (e, isMail) {
    if (!canFormat) return;
    var str = getSelected(e);
    var link = '';
    if (!isMail) {
        if (str.match(/^https?:/)) {
            link = str;
        } else if (str.match(/^(\w+\.)+\w{2,5}\/?/)) {
            link = 'http://' + str;
        } else if (str.match(/ /)) {
            link = 'http://';
        } else {
            link = 'http://' + str;
        }
    } else {
        if (str.match(/@/)) {
            link = str;
        }
    }
    var my_link = prompt(isMail ? 'Enter email address:' : 'Enter URL:', link);
    if (my_link != null) {
         if (str == '') str = my_link;
         if (isMail) my_link = 'mailto:' + my_link;
        setSelection(e, '<a href="' + my_link + '">' + str + '</a>');
    }
    return false;
}

function doCheckAll (f, v) {
    var e = f.id;
    if (e.value)
        e.checked = v;
    else
        for (i=0; i<e.length; i++) 
            e[i].checked = v;
}

function doCheckboxCheckAll (t) {
	var v = t.checked;
    var e = t.form.id;
    if (e.value)
        e.checked = v;
    else
        for (i=0; i<e.length; i++) 
            e[i].checked = v;
}

function execFilter(f) {
    if (f['filter-mode'].selectedIndex == 0) {  // no filter
        getByID('filter').value = '';
        getByID('filter_val').value = '';
        getByID('filter-form').submit();
    } else {
        var filter_col = f['filter-col'].options[f['filter-col'].selectedIndex].value;
        var filter_val = f[filter_col+'-val'].options[f[filter_col+'-val'].selectedIndex].value;
        getByID('filter').value = filter_col;
        getByID('filter_val').value = filter_val;
        getByID('filter-form').submit();
    }
    return false;
}

function setFilterVal(value) {
    var f = getByID('filter-select');
    if (f['filter-mode'].selectedIndex == 0) return;
    if (value == '') return;
    var filter_col = f['filter-col'].options[f['filter-col'].selectedIndex].value;
    if (filter_col) {
        var filter_fld = f[filter_col+'-val'];
        if (filter_fld.options) {
            for (var i = 0; i < filter_fld.options.length; i++) {
                if (filter_fld.options[i].value == value) {
                    filter_fld.selectedIndex = i;
                    var val_span = getByID("filter-text-val");
                    if (val_span) {
                        val_span.innerHTML = '<strong>' + filter_fld.options[i].text + '</strong>';
                    }
                    break;
                }
            }
        } else if (filter_fld.value) {
            filter_fld.value = value;
        }
    }
}

function toggleDisplayOptions() {
	var opt = TC.elementOrId('display-options');
	if (opt)
	{
		if (TC.hasClassName(opt, 'active'))
			TC.removeClassName(opt, 'active');
		else
			TC.addClassName(opt, 'active');
	}
	return false;
}

function tabToggle(selectedTab, tabs) {
        for (var i = 0; i < tabs.length; i++) {
                var tabObject = getByID(tabs[i] + '-tab');
                var contentObject = getByID(tabs[i] + '-panel');
                
                if (tabObject && contentObject) {
                        if (tabs[i] == selectedTab) {
                                tabObject.className = 'yah';
                                contentObject.style.display = 'block';
                        } else {
                                tabObject.className = 'default';
                                contentObject.style.display = 'none';
                        }
                }
        }
	return false;
}

function toggleSubPrefs(c) {
	var div = TC.elementOrId((c.name || c.id)+"-prefs") || TC.elementOrId((c.name || c.id)+'_prefs');
	if (div) {
		if (c.type) {
			var on = c.type == 'checkbox' ? c.checked : c.value != 0;
			div.style.display = on ? "block" : "none";
		} else {
			var on = div.style.display && div.style.display != "none";
			div.style.display = on ? "none" : "block";
		}
	}
	return false;
}

function toggleAdvancedPrefs(evt, c) {
	evt = evt || window.event;
	var id;
	var obj;
	if (!c || (typeof c != 'string')) {
		c = c || evt.target || evt.srcElement;
		id = c.id || c.name;
		obj = c;
	} else {
		id = c;
	}
	var div = getByID( id + '-advanced');
	if (div) {
		if (obj) {
			var shiftKey = evt ? evt.shiftKey : undefined;
        		if (evt && shiftKey && obj.type == 'checkbox')
				obj.checked = true;
			var on = obj.type == 'checkbox' ? obj.checked : obj.value != 0;
			if (on && shiftKey) {
				if (div.style.display == "block")
					div.style.display = "none";
				else
					div.style.display = "block";
			} else {
				div.style.display = "none";
			}
		} else {
			if (div.style.display == "block")
				div.style.display = "none";
			else
				div.style.display = "block";
		}
	}
	return false;
}

/*
function doBanIP(ip, blog_id, magic_token) {
	window.location = (ScriptURI
	  + "?__mode=save&_type=banlist"
	  + "&blog_id=" + blog_id
	  + "&magic_token=" + magic_token + "&ip=" + ip);
}
*/
