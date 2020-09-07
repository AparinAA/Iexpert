function validLoginForm (formId) {
	var form = document.getElementById(formId);
	form.addEventListener('submit', function (event) {
		event.preventDefault();
	});
}