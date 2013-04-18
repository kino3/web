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
こんにちは、<?php echo htmlspecialchars($_POST['name']); ?>さん。<br/>
<?php echo $_POST['sex']; ?><br/>
<?php echo $_POST['blood']; ?><br/>
<?php echo htmlspecialchars($_POST['kanso']); ?><br/>
<p><a href="form.html">入力にもどる</a></p>
</div>
</body>
</html>
