$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				category : $('#category').val()
			},
			type : 'POST',
			url : '/process2'
		})
		.done(function(data) {

				$('#successAlert').text(data.category).show();
		
		});

		event.preventDefault();

	});

});