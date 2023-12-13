function siliq_modal_show(url,title){
	$('#siliq_modal_title').text(title);
	$('#siliq_modal_content').text('Loading, please wait ...');
	$('#siliq_modal_content').load(url);
	$('#siliq_modal_windows').modal({show: true});
}

function siliq_modal_show_js(html,title){
	$('#siliq_modal_title').text(title);
	$("#siliq_modal_content").html(html);
	$('#siliq_modal_windows').modal({show: true});
}
