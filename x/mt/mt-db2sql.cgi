#!/usr/bin/perl -w

# Copyright 2001-2005 Six Apart. This code cannot be redistributed without
# permission from www.sixapart.com.  For more information, consult your
# Movable Type license.
#
# $Id: mt-db2sql.cgi 15432 2005-07-29 20:41:11Z bchoate $

use strict;
sub BEGIN {
    my $dir;
    require File::Spec;
    if (!($dir = $ENV{MT_HOME})) {
        if ($0 =~ m!(.*[/\\])!) {
            $dir = $1;
        } else {
            $dir = './';
        }
        $ENV{MT_HOME} = $dir;
    }
    unshift @INC, File::Spec->catdir($dir, 'lib');
    unshift @INC, File::Spec->catdir($dir, 'extlib');
}

local $| = 1;
print "Content-Type: text/html\n\n";
print "<pre>\n\n";

my @CLASSES = qw( MT::Author MT::Blog MT::Category MT::Comment MT::Entry
                  MT::IPBanList MT::Log MT::Notification MT::Permission
                  MT::Placement MT::Template MT::TemplateMap MT::Trackback
                  MT::TBPing MT::Session MT::PluginData MT::Config );

use File::Spec;

eval {
    local $SIG{__WARN__} = sub { print "**** WARNING: $_[0]\n" };

    require MT;
    my $mt = MT->new() or die MT->errstr;

    my $cfg = $mt->{cfg};
    require MT::Object;
    my($type) = $cfg->ObjectDriver =~ /^DBI::(.*)$/;
    MT::Object->set_driver('DBI::' . $type)
        or die MT::ObjectDriver->errstr;
    my $dbh = MT::Object->driver->{dbh};

    use MT::Upgrade;
    my @stmts;
    foreach (@CLASSES) {
        push @stmts, MT::Upgrade->check_class($_);
    }
    print "Loading database schema...\n\n";
    MT::Upgrade->do_upgrade(Install => 1);

    ## %ids will hold the highest IDs of each class.
    my %ids;

    print "Loading data...\n";
    for my $class (@CLASSES, 'MT::FileInfo' ) {
        print $class, "\n";
        MT::Object->set_driver('DBM');
        eval "use $class";
        my $iter = $class->load_iter;

        my %names;
        my %cat_parent;

        MT::Object->set_driver('DBI::' . $type);
        while (my $obj = $iter->()) {
            print "    ", $obj->id, "\n";
            # Update IDs only auto_increment.
            $ids{$class} = $obj->id
                if $obj->properties->{column_defs}->{id} =~ /auto_increment/ &&
                   (!$ids{$class} || $obj->id > $ids{$class});
            ## Look for duplicate template, category, and author names,
            ## because we have uniqueness constraints in the DB.
            if ($class eq 'MT::Template') {
                my $key = lc($obj->name) . $obj->blog_id;
                if ($names{$class}{$key}++) {
                    print "        Found duplicate template name '" .
                          $obj->name;
                    $obj->name($obj->name . ' ' . $names{$class}{$key});
                    print "'; renaming to '" . $obj->name . "'\n";
                }
                ## Touch the text column to make sure we read in
                ## any linked templates.
                my $text = $obj->text;
            } elsif ($class eq 'MT::Author') {
                my $key = lc($obj->name);
                if ($names{$class . $obj->type}{$key}++) {
                    print "        Found duplicate author name '" .
                          $obj->name;
                    $obj->name($obj->name . ' ' . $names{$class}{$key});
                    print "'; renaming to '" . $obj->name . "'\n";
                }
                $obj->email('') unless defined $obj->email;
                $obj->set_password('') unless defined $obj->password;
            } elsif ($class eq 'MT::Comment') {
                $obj->visible(1) unless defined $obj->visible;
            } elsif ($class eq 'MT::TBPing') {
                $obj->visible(1) unless defined $obj->visible;
            } elsif ($class eq 'MT::Category') {
                my $key = lc($obj->label) . $obj->blog_id;
                if ($names{$class}{$key}++) {
                    print "        Found duplicate category label '" .
                          $obj->label;
                    $obj->label($obj->label . ' ' . $names{$class}{$key});
                    print "'; renaming to '" . $obj->label . "'\n";
                }
                # save the parent value for assignment at the end
                if ($obj->parent) {
                    $cat_parent{$obj->id} = $obj->parent;
                    $obj->parent(0);
                }
            } elsif ($class eq 'MT::Trackback') {
                $obj->entry_id(0) unless defined $obj->entry_id;
                $obj->category_id(0) unless defined $obj->category_id;
            } elsif ($class eq 'MT::Entry') {
                $obj->allow_pings(0)
                    if defined $obj->allow_pings && $obj->allow_pings eq '';
                $obj->allow_comments(0)
                    if defined $obj->allow_comments && $obj->allow_comments eq '';
            }
            $obj->save
                or die $obj->errstr;
        }

        # fix up the category parents
        foreach my $id (keys %cat_parent) {
            my $cat = MT::Category->load($id);
            $cat->parent( $cat_parent{$id} );
            $cat->save;
        }

        print "\n";
    }

    if ($type eq 'postgres') {
        print "Updating sequences\n";
        my $dbh = MT::Object->driver->{dbh};
        for my $class (keys %ids) {
            print "    $class => $ids{$class}\n";
            my $seq = 'mt_' . $class->datasource . '_' .
                      $class->properties->{primary_key};
            $dbh->do("select setval('$seq', $ids{$class})")
                or die $dbh->errstr;
        }
    }

    $cfg->SchemaVersion(MT->schema_version(), 1);
    $cfg->save_config();
};
if ($@) {
    print <<HTML;

An error occurred while loading data:

$@

HTML
} else {
    print <<HTML;

Done copying data from Berkeley DB to your SQL database! All went well.

HTML
}

print "</pre>\n";
