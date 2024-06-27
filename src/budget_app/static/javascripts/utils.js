function countReused() {
	var cnt_aragon = $('#adm_aragon li').length;
	var cnt_spain = $('#adm_spain li').length;
	var cnt_orgs = $('#emp_org li').length;
	var cnt_int = $('#adm_int li').length;
	$('#adm_count_text').text('Ya sois ' + cnt_aragon + ' administraciones en Aragón, ' + cnt_spain + ' en España, '
			+ cnt_orgs + ' empresas y organizaciones y ' + cnt_int + ' entidad internacional. Y al resto de administraciones, ¡os esperamos!');
}