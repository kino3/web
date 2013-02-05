# Copyright 2001-2005 Six Apart. This code cannot be redistributed without
# permission from www.sixapart.com.  For more information, consult your
# Movable Type license.
#
# $Id: Plugin.pm 16586 2005-08-23 23:32:26Z bchoate $

package MT::Plugin;

use strict;

use MT::ErrorHandler;
@MT::Plugin::ISA = qw( MT::ErrorHandler );

# static method
sub select {
    my ($pkg, $class)  = @_;
    if ($class && $class !~ m/::/) {
        $class = $pkg . '::' . $class;
    } elsif (!$class) {
        $class = $pkg;
    }
    my @plugins;
    foreach (@MT::Plugins) {
        push @plugins, $_ if UNIVERSAL::isa($_, $class);
    }
    @plugins;
}

sub new {
    my $class = shift;
    my ($self) = ref$_[0] ? @_ : {@_};
    $self->{__settings} = {};
    bless $self, $class;
    $self->init();
    $self;
}

sub init {}
sub init_app {}
sub init_request {
    my $plugin = shift;
    delete $plugin->{__config_obj} if exists $plugin->{__config_obj};
}

sub _getset {
    $_ = (caller(1))[3]; s/.*:://;
    @_ > 1 ? $_[0]->{$_} = $_[1] : $_[0]->{$_}
}
sub key { &_getset }
sub name { &_getset }
sub author_name { &_getset }
sub author_link { &_getset }
sub plugin_link { &_getset }
sub version { &_getset }
sub config_link { &_getset }
sub doc_link { &_getset }
sub description { &_getset }
sub envelope { &_getset }
sub settings { &_getset }

sub load_config {
    my $plugin = shift;
    my ($param, $scope) = @_;
    my $setting_obj = $plugin->get_config_obj($scope);
    my $settings = $setting_obj->data;
    %$param = %$settings;
    foreach my $key (%$settings) {
        next unless defined $key;
        next unless exists $settings->{$key};
        my $value = $settings->{$key};
        next if !defined $value or $value =~ m/\s/ or length($value) > 100;
        $param->{$key.'_'.$value} = 1;
    }
}
sub save_config {
    my $plugin = shift;
    my ($param, $scope) = @_;
    my $pdata = $plugin->get_config_obj($scope);
    $scope =~ s/:.*//;
    my @vars = $plugin->config_vars($scope);
    my $data = $pdata->data() || {};
    foreach (@vars) {
        $data->{$_} = exists $param->{$_} ? $param->{$_} : undef;
    }
    $pdata->data($data);
    $pdata->save() or die $pdata->errstr;
}
sub reset_config {
    my $plugin = shift;
    my ($scope) = @_;
    my $obj = $plugin->get_config_obj($scope);
    $obj->remove if $obj->id;
}
sub config_template {
    my $plugin = shift;
    my ($param, $scope) = @_;
    if ($scope) {
        $scope =~ s/:.*//;
    } else {
        $scope = 'system';
    }
    if (my $tmpl = $plugin->{"${scope}_config_template"} || $plugin->{'config_template'}) {
        return $tmpl->($plugin, @_) if ref $tmpl eq 'CODE';
        if ($tmpl =~ /\s/) {
            return $tmpl;
        } else { # no spaces in $tmpl; must be a filename...
            return $plugin->load_tmpl($tmpl);
        }
    }
    return undef;
}
sub config_vars {
    my $plugin = shift;
    my ($scope) = @_;
    $scope ||= 'system';
    my @settings;
    if ($plugin->{settings}) {
        foreach my $setting (@{$plugin->{settings}}) {
            my ($name, $param) = @$setting;
            next if $scope && $param->{Scope} && $param->{Scope} ne $scope;
            push @settings, $name;
        }
    }
    @settings;
}
sub set_config_value {
    my $plugin = shift;
    my ($variable, $value, $scope) = @_;
    my $pdata_obj = $plugin->get_config_obj($scope);
    my $configuration = $pdata_obj->data() || {};
    $configuration->{$variable} = $value;
    $pdata_obj->data($configuration);
    $pdata_obj->save();
}

sub get_config_obj {
    my $plugin = shift;
    my ($scope_id) = @_;
    my $key;
    my $scope = $scope_id;
    if ($scope && $scope ne 'system') {
        $scope =~ s/:.*//; # strip off id, leave identifier
        $key = 'configuration:'.$scope_id;
    } else {
        $scope_id = 'system';
        $scope = 'system';
        $key = 'configuration';
    }
    return $plugin->{__config_obj}{$scope_id} if $plugin->{__config_obj}{$scope_id};
    require MT::PluginData;
    my $pdata_obj = MT::PluginData->load({plugin => $plugin->name(),
					  key => $key});
    if (!$pdata_obj) {
        $pdata_obj = MT::PluginData->new();
        $pdata_obj->plugin($plugin->name);
        $pdata_obj->key($key);
    }
    $plugin->{__config_obj}{$scope_id} = $pdata_obj;
    my $data = $pdata_obj->data() || {};
    $plugin->apply_default_settings($data, $scope_id);
    $pdata_obj->data($data);
    $pdata_obj;
}

sub apply_default_settings {
    my $plugin = shift;
    my ($data, $scope_id) = @_;
    my $scope = $scope_id;
    if ($scope =~ m/:/) {
        $scope =~ s/:.*//;
    } else {
        $scope_id = 'system';
    }
    my $defaults;
    if ($plugin->{settings} && ($defaults = $plugin->{settings}->defaults($scope))) {
        foreach (keys %$defaults) {
            $data->{$_} = $defaults->{$_}
                if (!exists $data->{$_}) && (!defined $data->{$_});
        }
    }
}

sub get_config_hash {
    my $plugin = shift;
    $plugin->get_config_obj(@_)->data() || {};
}

sub get_config_value {
    my $plugin = shift;
    my ($var, $scope) = @_;
    my $config = $plugin->get_config_hash($scope);
    return exists $config->{$_[0]} ? $config->{$_[0]} : undef;
}

sub load_tmpl {
    my $plugin = shift;
    my($file, @p) = @_;

    my $mt = MT->instance;
    my $path = $mt->{cfg}->TemplatePath;
    require HTML::Template;
    my $tmpl;
    my $err; 

    my @paths;
    my $dir = File::Spec->catdir($mt->mt_dir, $plugin->envelope, 'tmpl');
    push @paths, $dir if -d $dir;
    $dir = File::Spec->catdir($mt->mt_dir, $plugin->envelope);
    push @paths, $dir if -d $dir;
    if (my $alt_path = $mt->{cfg}->AltTemplatePath) {
        my $dir = File::Spec->catdir($path, $alt_path);
        if (-d $dir) {              # AltTemplatePath is relative
            push @paths, File::Spec->catdir($dir, $mt->{template_dir})
                if $mt->{template_dir};
            push @paths, $dir;
        } elsif (-d $alt_path) {    # AltTemplatePath is absolute
            push @paths, File::Spec->catdir($alt_path,
                                            $mt->{template_dir})
                if $mt->{template_dir};
            push @paths, $alt_path;
        }
    }
    push @paths, File::Spec->catdir($path, $mt->{template_dir})
        if $mt->{template_dir};
    push @paths, $path;
    my $cache_dir = File::Spec->catdir($path, 'cache');
    undef $cache_dir if (!-d $cache_dir) || (!-w $cache_dir);
    my $type = {'SCALAR' => 'scalarref', 'ARRAY' => 'arrayref'}->{ref $file}
        || 'filename';
    eval {
        $tmpl = HTML::Template->new(
            type => $type, source => $file,
            path => \@paths,
            search_path_on_include => 1,
            die_on_bad_params => 0, global_vars => 1,
            loop_context_vars => 1,
            $cache_dir ? (file_cache_dir => $cache_dir, file_cache => 1, file_cache_dir_mode => 0777) : (),
            @p);
    };
    $err = $@;
    return $plugin->error(
        $mt->translate("Loading template '[_1]' failed: [_2]", $file, $err))
        if $@;

    $tmpl->param(static_uri => $mt->static_path);
    $tmpl->param(script_path => $mt->path);
    $tmpl->param(mt_version => MT->version_id);

    $tmpl->param(language_tag => $mt->current_language);
    my $enc = $mt->{cfg}->PublishCharset ||
              $mt->language_handle->encoding;
    $tmpl->param(language_encoding => $enc);
    $mt->{charset} = $enc;

    if (my $author = $mt->{author}) {
        $tmpl->param(author_id => $author->id);
        $tmpl->param(author_name => $author->name);
    }

    ## We do this in load_tmpl because show_error and login don't call
    ## build_page; so we need to set these variables here.
    if (UNIVERSAL::isa($mt, 'MT::App')) {
        $tmpl->param(script_url => $mt->uri);
        $tmpl->param(mt_url => $mt->mt_uri);
        $tmpl->param(script_full_url => $mt->base . $mt->uri);
    }

    $tmpl;
}

package MT::PluginSettings;

sub new {
    my $pkg = shift;
    my ($self) = @_;
    bless $self, $pkg;
}

sub defaults {
    my $settings = shift;
    my ($scope) = @_;
    my $defaults = {};
    foreach my $setting (@$settings) {
        my ($name, $param) = @$setting;
        next unless exists $param->{Default};
        next if $scope && $param->{Scope} && $param->{Scope} ne $scope;
        $defaults->{$name} = $param->{Default};
    }
    $defaults;
}

1;
__END__

=head1 NAME

MT::Plugin - Movable Type class holding information that describes a
plugin

=head1 SYNOPSIS

    package MyPlugin;

    use base 'MT::Plugin';
    use vars qw($VERSION);
    $VERSION = 1.12;

    my $plugin = new MyPlugin({
        name => 'My Plugin',
        version => $VERSION,
        author_name => 'Conan the Barbaraian',
        author_link => 'http://example.com/',
        plugin_link => 'http://example.com/mt-plugins/example/',
        description => 'Frobnazticates all Diffyhorns',
        config_link => 'myplugin.cgi',
        settings => new MT::PluginSettings([
            ['option1', { Default => 'default_setting' }],
            ['option2', { Default => 'system_default', Scope => 'system' }],
            ['option2', { Scope => 'blog' }],
        ],
        config_template => \&config_tmpl
    });
    MT->add_plugin($plugin);

    # Alternatively, instantiating MT::Plugin itself

    my $plugin = new MT::Plugin({
        name => "Example Plugin",
        version => 1.12,
        author_name => "Conan the Barbarian",
        author_link => "http://example.com/",
        plugin_link => "http://example.com/mt-plugins/example/",
        description => "Frobnazticates all Diffyhorns",
        config_link => 'myplugin.cgi',
        doc_link => <documentation URL>,
        settings => new MT::PluginSettings([
            ['option1', { Default => 'default_setting' }],
            ['option2', { Default => 'system_default', Scope => 'system' }],
            ['option2', { Scope => 'blog' }],
        ],
        config_template => \&config_tmpl
    });
    MT->add_plugin($plugin);

=head1 DESCRIPTION

An I<MT::Plugin> object holds data about a plugin which is used to help
users understand what the plugin does and let them configure the
plugin.

Normally, a plugin will construct an I<MT::Plugin> object and pass it
to the C<add_plugin> method of the I<MT> class:

    MT->add_plugin($plugin);

This will insert a slug for that plugin on the main MT page; the slug
gives the name and description and provides links to the documentation
and configuration pages, if any.

When adding callbacks, you will use the plugin object as well; this
object is used to help the user identify errors that arise in
executing the callback. For example, to add a callback which is
executed before the I<MT::Foo> object is saved to the database, you might
make a call like this:

   MT::Foo->add_callback("pre_save", 10, $plugin, \&callback_function);

This call will tell I<MT::Foo> to call the function
C<callback_function> just before executing any C<save> operation. The
number '10' is signalling the priority, which controls the order in
which various plugins are called. Lower number callbacks are called
first.

=head1 ARGUMENTS

=over 4

=item * name

A human-readable string identifying the plugin. This will be displayed
in the plugin's slug on the MT front page.

=item * version (optional, but recommended)

The version number for the release of the plugin. Will be displayed
next to the plugin's name wherever listed.

=item * description (optional)

A longer string giving a brief description of what the plugin does.

=item * doc_link (optional)

A URL pointing to some documentation for the plugin. This can be a
relative path, in which case it identifies documentation within the
plugin's distribution, or it can be an absolute URL, pointing at
off-site documentation.

=item * config_link (optional)

The relative path of a CGI script or some other configuration
interface for the plugin. This is relative to the "plugin
envelope"--that is, the directory underneath C<mt/plugins> where all
your plugin files live.

=item * author_name (optional)

The name of the individual or company that created the plugin.

=item * author_link (optional)

A URL pointing to the home page of the individual or company that
created the plugin.

=item * plugin_link (optional)

A URL pointing to the home page for the plugin itself.

=item * config_template (optional)

=item * system_config_template (optional)

=item * blog_config_template (optional)

=item * settings (optional)

Identifies the plugin's configuration settings.

=head1 Methods

Each of the above arguments to the constructor is also a 'getter'
method that returns the corresponding value. C<MT::Plugin> also offers
the following methods:

=head2 $plugin->init_app

For subclassed MT::Plugins that declare this method, it is invoked when
the application starts up.

=head2 $plugin->init_request

For subclassed MT::Plugins that declare this method, it is invoked when
the application begins handling a new request.

=head2 $plugin->envelope

Returns the path to the plugin, relative to the MT directory. This is
determined automatically when the plugin is loaded.

=head2 $plugin->set_config_value($key, $value[, $scope])

=head2 $plugin->get_config_value($key[, $scope])

These routines facilitate easy storage of simple configuration
options.  They make use of the PluginData table in the database to
store a set of key-value pairs for each plugin. Call them as follows:

    $plugin->set_config_value($key, $value);
    $value = $plugin->get_config_value($key);

The C<name> field of the plugin object is used as the namespace for
the keys. Thus it would not be wise for one plugin to use the
same C<name> as a different plugin.

=head2 $plugin->get_config_obj([$scope])

Retrieves the MT::PluginData object associated with this plugin
and the scope identified (which defaults to 'system' if unspecified).

=head2 $plugin->get_config_hash([$scope])

Retrieves the configuration data associated with this plugin
and returns it a a Perl hash reference. If the scope parameter is not given,
the 'system' scope is assumed.

=head2 $plugin->config_template($params[, $scope])

Called to retrieve a HTML::Template object which will be output as the
configuration form for this plugin. Optionally a scope may be specified
(defaults to 'system').

    my $system_tmpl = $plugin->config_template($params, 'system');
    my $system_tmpl = $plugin->config_template($params);
    my $blog_tmpl = $plugin->config_template($params, 'blog:1');

=head2 $plugin->config_vars([$scope])

Returns an array of configuration setting names for the requested scope.

=head2 $plugin->save_config($param[, $scope])

Handles saving configuration data from the plugin configuration form.

    my $param = { 'option1' => 'x' };
    $plugin->save_config($param); # saves system configuration data
    $plugin->save_config($param, 'system'); # saves system configuration data
    $plugin->save_config($param, 'blog:1'); # saves blog configuration data

=head2 $plugin->load_config($param[, $scope])

Handles loading configuration data from the plugindata table.

=head2 $plugin->load_tmpl($file[, ...])

Used to load a HTML::Template object relative to the plugin's directory.
It will scan both the plugin's directory and a directory named 'tmpl'
underneath it. It will passthrough parameters that follow the $file
parameter into the HTML::Template constructor.

=head1 MT::PluginSettings

The MT::PluginSettings package is also declared with this module. It
is used to define a group of settings and their defaults for the plugin.
These settings are processed whenever configuration data is requested
from the plugin.

Example:

    $plugin->{settings} = new MT::PluginSettings([
        ['option1', { Default => 'default_setting' }],
        ['option2', { Default => 'system_default', Scope => 'system' }],
        ['option2', { Scope => 'blog' }],
    ]);

Settings can be assigned a default value and an applicable 'scope'.
Currently, recognized scopes are "system" and "blog".

=head1 AUTHOR & COPYRIGHTS

Please see the I<MT> manpage for author, copyright, and license information.

=cut
