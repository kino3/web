# pmHeadChanger
package MT::Plugin::pmHeadChanger;
use vars qw( $VERSION );
$VERSION = 1.2;
require MT::Plugin;
my $plugin = MT::Plugin->new({
	name => "pmHeadChanger",
	author_name => 'pmLabo.',
	author_link => 'http://www.pmlabo.com/',
	version => $VERSION
});
MT->add_plugin($plugin);

use MT::Template::Context;

MT::Template::Context->add_global_filter(pmhc => \&Replace_title);

sub Replace_title{
	my ($str, $arg, $ctx) = @_;
	if($arg){ $str =~ s/^\d+(\)|\-)/$arg/; }else{ $str =~ s/^\d+(\)|\-)//; }
	return $str;
}
1;
