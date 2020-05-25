
document.addEventListener('DOMContentLoaded', (event) => {
	fetch('http://localhost:5000/api/analytics', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ page: window.location.pathname })
	})
		.then(response => {
			console.log(response);
			return response.json()
		})
		.then(data => {
			console.log('Success:', data);
		})
		.catch((error) => {
			console.error('Error:', error);
		});	
});
/*

fetch('http://localhost:5000/api/messages', {
	method: 'POST',
	headers: {
		'Content-Type': 'application/json',
	},
	body: JSON.stringify(data)
})
	.then(response => {
		console.log(response);
		return response.json()
	})
	.then(data => {
		console.log('Success:', data);
	})
	.catch((error) => {
		console.error('Error:', error);
	});*/