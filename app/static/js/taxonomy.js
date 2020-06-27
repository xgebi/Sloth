document.addEventListener('DOMContentLoaded', (event) => {
    // delete-taxonomy
    fetch('/api/post/taxonomy', {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
			'authorization': document.cookie
                                .split(';')
                                .find(row => row.trim().startsWith('sloth_session'))
                                .split('=')[1],
            'body': JSON.stringify({
                uuid: document.querySelector("#uuid").value
            })
		}
	})
		.then(response => {
			window.location.replace(window.location.href.substring(0, window.location.href.lastIndexOf("/")));
		})
		.catch((error) => {
			console.error('Error:', error);
		});

    // display-name
    document.querySelector("#display-name").addEventListener('blur', (event)=> {
        document.querySelector("#slug").value = event.target?.value.trim().replace(/\s+/g, '-');
    })
});