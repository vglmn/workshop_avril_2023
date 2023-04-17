<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PHP Test</title>
</head>
<body>
    <form action="phptest.php" method="post">
    <center><label for="seed">Amorce</label><input type="text" id="seed" name="seed"><br/>
        <label for="temp">Température</label><input type="range" min="0.1" max="100" value="50" class="slider" id="temp" name="temp"></center>
    <hr/>
        <?php

            if(strlen($_POST["seed"]) > 0 && $_POST["temp"] > 0) {
                $tuCurl = curl_init();
                curl_setopt($tuCurl, CURLOPT_URL, "http://localhost:8280/conte");
                curl_setopt($tuCurl, CURLOPT_POST, 1);
                curl_setopt($tuCurl, CURLOPT_HTTPHEADER, array("Content-Type: application/json"));
                $data = json_encode(array('seed' => $_POST["seed"], "temp" => $_POST["temp"] / 100, "size" => 150));
                echo("<!-- ".$data." -->");
                curl_setopt($tuCurl, CURLOPT_POSTFIELDS, $data);
                curl_setopt($tuCurl, CURLOPT_RETURNTRANSFER, TRUE);
                $tuData = curl_exec($tuCurl);
                if(!curl_errno($tuCurl)) {
                    echo("<div id=\"result\">$tuData</div>");
                } else {
                    echo("<div id=\"result\">".curl_error($tuCurl)."</div>");
                }
                echo("<!-- ".implode("|",curl_getinfo($tuCurl))." -->");
                echo("<!-- ".curl_error($tuCurl)." -->");
                curl_close($tuCurl);
            } else {
                echo("<div id=\"result\">Tapez un truc</div>");
            }

         ?>
    <hr/>
    <button type="submit">Click me!</button>
    </form>
</body>
</html>