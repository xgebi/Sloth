document.querySelector("#delete-message").addEventListener('click', (event) => {
	fetch('/api/messages/delete', {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
			'authorization': document.cookie
			.split(';')
		  	.find(row => row.trim().startsWith('sloth_session'))
		  	.split('=')[1]
		},
        body: JSON.stringify({message_uuid: window.location.pathname.substring(window.location.pathname.lastIndexOf("/") + 1)})
	})
		.then(response => {
			if (response.ok) {
                window.location.replace(window.location.href.substring(0, window.location.href.lastIndexOf("/")));
            }
            throw `${response.status}: ${response.statusText}`
		})
		.catch((error) => {
			console.error('Error:', error);
		});
});