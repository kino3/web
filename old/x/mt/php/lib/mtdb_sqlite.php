<?php
# Copyright 2001-2005 Six Apart. This code cannot be redistributed without
# permission from www.sixapart.com.  For more information, consult your
# Movable Type license.
#
# $Id: mtdb_sqlite.php 15432 2005-07-29 20:41:11Z bchoate $

require_once("ezsql".DIRECTORY_SEPARATOR."ezsql_sqlite.php");
require_once("mtdb_base.php");

class MTDatabase_sqlite extends MTDatabaseBase {
    var $vendor = 'sqlite';
    function MTDatabase_sqlite($dbuser, $dbpassword, $dbname, $dbhost, $dbport) {
        parent::MTDatabaseBase($dbname);
    }
}
?>
