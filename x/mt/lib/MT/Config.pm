# Copyright 2001-2005 Six Apart. This code cannot be redistributed without
# permission from www.sixapart.com.  For more information, consult your
# Movable Type license.
#
# $Id: Config.pm 15432 2005-07-29 20:41:11Z bchoate $

package MT::Config;
use strict;

use MT::Object;
@MT::Config::ISA = qw( MT::Object );
__PACKAGE__->install_properties({
    column_defs => {
        'id' => 'integer not null auto_increment',
        'data' => 'text',
    },
    primary_key => 'id',
    datasource => 'config',
});

1;

__END__

=pod

=head1 NAME

MT::Config - Installation-wide configuration data.

=cut
