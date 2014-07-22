<?php
header('Content-Type: application/json');

$respuesta = array();
$link = mysql_connect("localhost","root","1qazxsw2","control_diio") or die("Error " . mysqli_error($link));
//DEFINIR VARIABLES GLOBALES DE CONEXION
mysql_set_charset('utf8');

$query = "SELECT ID,FECHA,FECHA_MONITOR,BASTON,RFID FROM control_diio.RFID_LECTURA WHERE ESTADO != 'L' AND BASTON = (SELECT VALOR FROM control_diio.RFID_PARAMETROS WHERE PARAMETRO = '".$_GET['baston']."') ORDER BY FECHA";

//VERIFICAR OPCIONES RECIBIDAS
if ( isset ( $_GET ) && $_GET['opcion'] == 'bastones' ) {
	$query = "SELECT PARAMETRO AS NOMBRE FROM control_diio.RFID_PARAMETROS WHERE PARAMETRO like '%BASTON%'";
}

if ( isset ( $_GET ) && $_GET['opcion'] == 'obtener' )  {
    if ( array_key_exists('baston',$_GET) ) {
		$query = "SELECT ID,FECHA,FECHA_MONITOR,BASTON,RFID FROM control_diio.RFID_LECTURA WHERE ESTADO !=  'L' AND BASTON = (SELECT VALOR FROM control_diio.RFID_PARAMETROS WHERE PARAMETRO = '".$_GET['baston']."') ORDER BY FECHA LIMIT 1"; 
	}
	else {
		$dato["RESP"] = "ERROR: Debe especificar el nombre de un Baston";
		array_push($respuesta,$dato);
		echo json_encode($respuesta);
		exit;
	}
}
if ( isset ( $_GET ) && $_GET['opcion'] == 'leido' ) {
	if ( array_key_exists('id',$_GET) ) {
		$query = "UPDATE control_diio.RFID_LECTURA SET ESTADO = 'L' WHERE ID = ".$_GET['id'];
		$result = mysql_query($query) or die('Consulta fallida: '.$query.':'. mysql_error());
		$dato["RESP"] = "OK";
	}
	else {
		$dato["RESP"] = "ERROR: Debe especificar el ID de RFID ya procesado";
	}	
	array_push($respuesta,$dato);
	echo json_encode($respuesta);
	exit;
}

if ( isset ( $_GET ) && $_GET['opcion'] == 'terminado' ) {
	if ( !array_key_exists('baston',$_GET) ) {
		$dato["RESP"] = "ERROR: Debe especificar el baston utilizado para las Lecturas";
		array_push($respuesta,$dato);
		echo json_encode($respuesta);
		exit;
	}
	$query = "SELECT COUNT(*) FROM control_diio.RFID_LECTURA WHERE ESTADO = 'N' AND BASTON = (SELECT VALOR FROM control_diio.RFID_PARAMETROS WHERE PARAMETRO = '".$_GET['baston']."') ";
	$result = mysql_query($query) or die('Consulta fallida: '.$query.':'. mysql_error());
	$data = mysql_fetch_array($result);
	if ( $data[0] != '0' ) {
		$dato["RESP"] = "ERROR: Existen (".$data[0].") RFID No procesados";
	}
	else {
		$query = "DELETE FROM control_diio.RFID_LECTURA WHERE BASTON = (SELECT VALOR FROM control_diio.RFID_PARAMETROS WHERE PARAMETRO = '".$_GET['baston']."') ";
		$result = mysql_query($query) or die('Consulta fallida: '.$query.':'. mysql_error());
		$dato["RESP"] = "OK";
	}
	array_push($respuesta,$dato);
	echo json_encode($respuesta);
	exit;
}

//CREACION DE RESPUESTA JSON
$result = mysql_query($query) or die('Consulta fallida: '.$query.':'. mysql_error());
$respuesta = array();
while ( $data = mysql_fetch_assoc($result) ) {
    $dato = null;
    $keys = array_keys($data);
    foreach ( $keys as $key){
        $dato[$key] = $data[$key];
    }
    array_push($respuesta,$dato);
}
echo json_encode($respuesta);
?>
