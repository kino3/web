# Copyright 2001-2005 Six Apart. This code cannot be redistributed without
# permission from www.sixapart.com.  For more information, consult your
# Movable Type license.
#
# $Id: Upgrader.pm 16380 2005-08-18 19:42:14Z bchoate $

package MT::App::Upgrader;
use strict;

use MT::App;
@MT::App::Upgrader::ISA = qw(MT::App);
use MT::BasicAuthor;
use MT::Util;
use MT::I18N;
use JSON;

use vars qw($MAX_TIME);
sub BEGIN {
    $MAX_TIME = 5;
}

sub init {
    my $app = shift;
    $app->SUPER::init(@_) or return;
    $app->add_methods(
        'main' => \&main,
        'install' => \&upgrade,
        'upgrade' => \&upgrade,
        'run_actions' => \&run_actions,
    );
    $app->{user_class} = 'MT::BasicAuthor';
    $app->{template_dir} = 'cms';
    $app->{plugin_template_path} = '';
    $app;
}

sub init_request {
    my $app = shift;
    $app->SUPER::init_request(@_);
    $app->{default_mode} = 'main';
    my $mode = $app->mode;
    $app->{requires_login} = $mode ne 'install' && $mode ne 'run_actions';
#    $app->{requires_login} = 0;
}

sub login {
    my $app = shift;
    my $q = $app->{query};
    my $cookies = $app->{cookies};
    my($user, $pass, $remember, $crypted, $cookie_middle);
    my $first_time = 0;
    my $cookie_name = $app->user_cookie;
    if ($cookies->{$cookie_name}) {
        ($user, $cookie_middle, $remember) = split /::/, $cookies->{$cookie_name}->value;
    } elsif ($cookies->{'user'}) {   # 1.1 - 2.661
        ($user, $cookie_middle, $remember) = split /::/, $cookies->{'user'}->value;
    }
    if ($q->param('username') && $q->param('password')) {
        $first_time = 1;
        $user = $q->param('username');
        $pass = $q->param('password');
        $crypted = 0;
    }
    return unless $user && ($pass || $cookie_middle);
    if (my @author = MT::BasicAuthor->load({ name => $user })) {
        foreach my $author (@author) {
            # skip any possible non-authors...
            next unless $author->password;
            next if $author->password eq '(none)';
            my $valid = 0;
            if ($pass) {
                if ($author->is_valid_password($pass, $crypted)) {
                    $app->request('fresh_login', 1);
                    $valid = 1;
                }
            } elsif ($cookie_middle) {
                # try checking old-style cookie using crypt'd password
		# then try the magic token if user is using new cookie
		# format...
                if ($author->is_valid_password($cookie_middle, 1)) {
                    $valid = 1;
                } elsif ($cookie_middle eq $author->magic_token) {
                    $valid = 1;
                } elsif (eval{require MT::BasicSession;MT::BasicSession->load($cookie_middle)}) {
                    $valid = 1;
                }
            }
            if ($valid) {
                $app->{author} = $author;
                if ($cookie_middle ne $author->magic_token) {
                    my %arg = (-name => $cookie_name,
                               -value => join('::',
                                              $author->name,
                                              $author->magic_token,
                                              # note this is BasicAuthor::magic_token
                                              $remember),
                               -path => $app->mt_path
                               );
                    $app->bake_cookie(%arg);
                }
                return($author, $first_time);
            } else {
                return undef;    # error message?
            }
        }
    }
    ## Login invalid, so get rid of cookie (if it exists) and let the
    ## user know.
    $app->bake_cookie(-name => $cookie_name, -value => '',
        -expires => '-1y', -path => $app->mt_path)
        unless $first_time;
    return $app->error($app->translate('Invalid login.'));
}

# build_page needs to know what to use as the magic token
sub current_magic {
    my $app = shift;
    return $app->{author}->magic_token if $app->{author};
}

sub upgrade {
    my $app = shift;

    my $install_mode;

    my $driver = MT::Object->driver;
    if (!$driver || !$driver->table_exists('MT::Author')) {
        $install_mode = 1;
        my $method = $app->request_method;
        if ($method ne 'POST') {
            return $app->build_page("install.tmpl");
        }
    } else {
        $app->validate_magic or return;
    }

    my $steps;
    eval {
        local $app->{upgrading} = 1;
        require MT::Upgrade;
        MT::Upgrade->do_upgrade(Install => $install_mode, DryRun => 1,
            App => $app);
        my $steps = $app->response->{steps};
        my $fn = \%MT::Upgrade::functions;
        if ($steps && @$steps) {
            @$steps = sort { $fn->{$a->[0]}->{priority} <=>
                             $fn->{$b->[0]}->{priority} } @$steps;
        }
    };
    die $@ if $@;
    $steps = $app->response->{steps};
    my $json_steps;
    if ($steps && @$steps) {
        $json_steps = objToJson($steps);
    }

    my $param = {
        installing => $install_mode,
        up_to_date => $json_steps ? 0 : 1,
        initial_steps => $json_steps,
    };

    return $app->build_page('upgrade_runner.tmpl', $param);
}

sub finish {
    my $app = shift;

    $app->login;
    if ($app->{author}) {
        require MT::Author;
        my $author = MT::Author->load($app->{author}->id);
        my $cookie_obj = $app->start_session($author);
        my $response = $app->response;
        $response->{cookie} = { map { $_ => $cookie_obj->{$_} } (keys %$cookie_obj) };
        $app->log($app->translate("User [_1] upgraded database to version [_2]", $app->{author}->name, MT->schema_version));
    }    
}


sub get_actions {
    my $app = shift;
    my $updated;

    my $install_mode;
    my $driver = MT::Object->driver;
    if (!$driver || !$driver->table_exists('MT::Author')) {
        $install_mode = 1;
    }

    eval {
        local $app->{upgrading} = 1;
        require MT::Upgrade;
        MT::Upgrade->do_upgrade(Install => $install_mode, DryRun => 1,
            App => $app);
        my $steps = $app->response->{steps};
        my $fn = \%MT::Upgrade::functions;
        if ($steps && @$steps) {
            @$steps = sort { $fn->{$a->[0]}->{priority} <=>
                             $fn->{$b->[0]}->{priority} } @$steps;
        }
    };
    $app->error($@) if $@;
    $app->json_response;
}

sub run_actions {
    my $app = shift;

    $| = 1;

    $app->{no_print_body} = 1;
    $app->send_http_header('text/plain');

    my $install_mode = $app->param('installing');

    if (!$install_mode) {
        $app->login;
    }

    my $schema = $app->{cfg}->SchemaVersion || 0;
    if ($schema) {
        if (!$app->validate_magic) {
            $app->response->{error} = $app->translate("Invalid session.");
            return $app->json_response;
        }
    }

    my $steps = $app->param('steps');
    $steps = jsonToObj($steps);

    my $start = time;
    my @steps = ( @$steps );
    my $step;

    my $fn = \%MT::Upgrade::functions;

    eval {
        local $app->{upgrading} = 1;
        require MT::Upgrade;
        local $MT::Upgrade::App = $app;
        local $MT::Upgrade::Installing = $install_mode;
        local $MT::Upgrade::MAX_TIME = $MAX_TIME;

        while ($step = shift @steps) {
            MT::Upgrade->run_step($step) or last;
            my $new_steps = $app->response->{steps};
            if (@$new_steps) {
                push @steps, @$new_steps;
                @steps = sort { $fn->{$a->[0]}->{priority} <=>
                                 $fn->{$b->[0]}->{priority} } @steps;
                $app->response->{steps} = [];
            }
            # don't run for more than our time limit
            last if time > $start + $MAX_TIME; 
        }
    };
    if ($@) {
        unshift @steps, $step if $step;
        $app->response->{error} = $@;
    }
    if ($app->errstr =~ m/\w/) {
        unshift @steps, $step;
        $app->response->{error} = $app->errstr;
    }

    if (@steps) {
        @steps = sort { $fn->{$a->[0]}->{priority} <=>
                         $fn->{$b->[0]}->{priority} } @steps;
        $app->response->{steps} = \@steps;
    }

    $app->json_response;
}

sub json_response {
    my $app = shift;
    my $res = $app->response;
    my $json = objToJson($res);
    $app->print( ' JSON:' . $json);
}

sub response {
    my $self = shift || MT->instance;
    if (!$self->{response}) {
        $self->{response} = { steps => [], progress => [], error => undef };
    }
    $self->{response};
}

sub add_step {
    my $self = shift;
    push @{ $self->response->{steps} }, [ @_ ];
}

sub progress {
    my $app = shift;
    my ($msg, $make_id) = @_;
    $msg =~ s/^\s+//gs;
    $msg =~ s/\s+$//gs;
    $msg =~ s/\s+/ /gs;
    if ($make_id) {
        require MT::Util;
        my $id = MT::Util::dirify($make_id);
        $msg = qq{#$id $msg};
    }
    $app->print($msg . "\n");
}

sub error {
    my $app = shift;
    my ($msg) = @_;
    $app->SUPER::error(@_);
    $app->response->{error} = $msg;
    die $msg if ref $app && $app->{upgrading};
    return;
}

sub main {
    my $app = shift;

    my $driver = MT::Object->driver;
    if (!$driver || !$driver->table_exists('MT::Author')) {
        my $method = $app->request_method;
        if ($method ne 'POST') {
            return $app->build_page("install.tmpl");
        }
        $app->validate_magic or return;
        return $app->upgrade();
    }

    my $schema = $app->{cfg}->SchemaVersion || 0;
    if ($schema >= 3.2) {
        my $author;
        eval {
            require MT::Author;
            $author = MT::Author->load($app->{author}->id);
        };
        if ($author && !$author->is_superuser) {
            return $app->errtrans("No permissions. Please contact your administrator for upgrading Movable Type.");
        }
    }
    $app->build_page('upgrade.tmpl');
}

sub build_page {
    my $app = shift;
    my ($tmpl, $param) = @_;
    $param ||= {};
    $param->{no_breadcrumbs} = 1;
    $app->SUPER::build_page($tmpl, $param);
}

1;
