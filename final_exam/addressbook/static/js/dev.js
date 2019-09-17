$( document ).ready(function() {

	var csrftoken = $("[name=csrfmiddlewaretoken]").val();
	
	function csrfSafeMethod(method) {
    	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	}

	$.ajaxSetup({
    	beforeSend: function(xhr, settings) {
        	if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            	xhr.setRequestHeader("X-CSRFToken", csrftoken);
        	}
    	}
	});


	$('#contact-form').submit(function(event) {
		event.preventDefault();
		
		var form_id = '#contact-form';
		var url = '/contact/add/';
		var success_msg = 'Contact successfully created!';
		ajax_contact(form_id, url, success_msg);
		$(this).trigger('reset');

	});

	$('#contact-update').submit(function(event) {
		event.preventDefault();
		
		var form_id = '#contact-update';
		var url = window.location.pathname;
		var success_msg = 'Contact successfully updated!';
		ajax_contact(form_id, url, success_msg);

	});

	function ajax_contact(form_id, url, msg){

		var data = {
			first_name: $(form_id).find('#id_first_name').val(),
			last_name: $(form_id).find('#id_last_name').val(),
			contact_number: $(form_id).find('#id_contact_number').val(),
			address: $(form_id).find('#id_address').val(),
		}

		$.ajax({
		    url:  url,
		    type:  'POST',
		    data: data,
		    success: function (data){
		    	toastr.success(msg);
		    },
		    error: function (data){
		    	toastr.error('Invalid contact details.');
		    }
		});
	}

});