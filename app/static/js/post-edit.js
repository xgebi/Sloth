 const post = {

 };

const gallery = {
	_items: [],
	get images() {
		return this._items;
	},
	set images(images) {
		this._items = images;
	}
};

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
			gallery.images = data.media;
		})
		.catch((error) => {
			console.error('Error:', error);
		});

	document.querySelector("#gallery-opener").addEventListener('click', () => {
		openGalleryDialog(gallery.images);
	})

    // 2. publish post button
	document.querySelector("#publish-button").addEventListener('click', publishPost);

	// 3. save draft button
	document.querySelector("#save-draft").addEventListener('click', saveDraft);

	// 4. update button
	document.querySelector("#update-button").addEventListener('click', updatePost);
});

function openGalleryDialog(data) {
	debugger;
	const dialog = document.querySelector("#modal");
	dialog.setAttribute('open', '');
	const copyResult = document.createElement('p');
	dialog.appendChild(copyResult);
	const mediaSection = document.createElement('section')
	gallery.images.forEach((item) => {
		const wrapper = document.createElement('article');
		wrapper.setAttribute('style', "width: 50px; height: 80px");
		// uuid, file_path, alt
		const image = document.createElement('img');
		image.setAttribute('src', item['filePath']);
		image.setAttribute('alt', item["alt"])
		wrapper.appendChild(image);

		const copyUrlButton = document.createElement('button');
		copyUrlButton.textContent = 'Copy URL'
		copyUrlButton.addEventListener('click', () => {
			copyResult.textContent = '';
			navigator.clipboard.writeText(item['filePath']).then(function() {
			  	/* clipboard successfully set */
				copyResult.textContent = 'URL copied to clipboard';
			}, function() {
			  	/* clipboard write failed */
				copyResult.textContent = 'Error copying URL to clipboard';
			});
		});
		wrapper.appendChild(copyUrlButton);

		mediaSection.appendChild(wrapper);
	});
	dialog.appendChild(mediaSection);
	const closeButton = document.createElement('button');
	closeButton.textContent = 'Close'
	closeButton.addEventListener('click', () => {
		debugger;
		while (dialog.firstChild) {
    		dialog.removeChild(dialog.lastChild);
  		}
		dialog.removeAttribute('open');
	});
	dialog.appendChild(closeButton);
}

function publishPost() {
	const values = collectValues();
	savePost("", values);
}
function saveDraft() {
	const values = collectValues();
	savePost("", values);
}
function updatePost() {
	const values = collectValues();
	savePost("", values);
}
function collectValues() {}

function savePost(status, values) {
	let uri;
	if (status === 'new') {
		uri = '/api/post/new';
	} else if (status === 'scheduled') {
		uri = '/api/post/schedule';
	} else if (status === 'update') {
		uri = '/api/post/updated';
	} else if (status === 'publish') {
		uri = '/api/post/publish';
	} else {
		return;
	}
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
			gallery.images = data.media;
		})
		.catch((error) => {
			console.error('Error:', error);
		});
}