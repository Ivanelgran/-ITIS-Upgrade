$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				inputDate : $('#inputDate').val(),
				outputDate : $('#outputDate').val()
			},
			type : 'POST',
			url : '/process'
		})
		.done(function(data) {
			
				$('#successAlert').text(data.inputDate).show();
		});

		event.preventDefault();

	});

});