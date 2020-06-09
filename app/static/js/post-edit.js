document.addEventListener('DOMContentLoaded', (event) => {
    // 1. get gallery
	fetch('/api/post/media', {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'authorization': document.cookie
			.split(';')
		  	.find(row => row.trim().startsWith('sloth_session'))
		  	.split('=')[1]
		}
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

    // 2. deal with submit button
});