
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

function sendMessage(name, email, body, captcha) {
	if (captcha?.length > 0) {
		return;
	}
	fetch('http://localhost:5000/api/messages', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			name: name,
			email: email,
			body: body
		})
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
}

function sendDummyMessage() {
	sendMessage("Bill", "bill@dead.is", "some body", "");
}

document.querySelector("#send-message").addEventListener('click', sendDummyMessage);