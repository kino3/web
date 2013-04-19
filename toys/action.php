<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title></title>
<meta name="keywords" content="">
<meta name="description" content="">
<link rel="stylesheet" href="../common/style.css" media="all">
</head>
<body>
<div class="small">
<?php
$con = mysql_connect("localhost","kino","7hueychan");
if (!$con)
  {
  die('Could not connect: ' . mysql_error());
  }

mysql_select_db("kino", $con);

$sql="INSERT INTO sample
VALUES
('$_POST[name]','$_POST[sex]','$_POST[blood]','$_POST[kanso]')";

if (!mysql_query($sql,$con))
  {
  die('Error: ' . mysql_error());
  }
echo "1 record added";

mysql_close($con)
?><br/>
こんにちは、<?php echo htmlspecialchars($_POST['name']); ?>さん。<br/>
<?php echo $_POST['sex']; ?><br/>
<?php echo $_POST['blood']; ?><br/>
<?php echo htmlspecialchars($_POST['kanso']); ?><br/>
<p><a href="form.html">入力にもどる</a></p>
</div>
</body>
</html>
