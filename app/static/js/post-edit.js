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
	document.querySelector("#publish-button")?.addEventListener('click', publishPost);

	// 3. save draft button
	document.querySelector("#save-draft")?.addEventListener('click', saveDraft);

	// 4. update button
	document.querySelector("#update-button")?.addEventListener('click', updatePost);

	// 5. schedule button
	document.querySelector("#schedule-button")?.addEventListener('click', schedulePost);

	document.querySelector("#title").addEventListener('blur', (event)=> {
        document.querySelector("#slug").value = event.target?.value.trim().replace(/\s+/g, '-');
    });

	document.querySelector("#create-category")?.addEventListener('click', createCategory);
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
	values["action"] = "publish";
	savePost(values);
}

function schedulePost() {
	const values = collectValues();
	values["action"] = "schedule";
	savePost(values);
}

function saveDraft() {
	const values = collectValues();
	values["action"] = "save_draft";
	savePost(values);
}
function updatePost() {
	const values = collectValues();
	values["action"] = "update";
	savePost(values);
}
function collectValues() {
	const post = {};
	post["uuid"] = document.querySelector("#uuid").dataset["uuid"];
	post["post_type_uuid"] = document.querySelector("#uuid").dataset["posttypeUuid"];
	post["title"] = document.querySelector("#title").value;
	post["slug"] = document.querySelector("#slug").value;
	post["excerpt"] = document.querySelector("#excerpt").value;
	post["content"] = document.querySelector("#content").value;
	post["css"] = document.querySelector("#css").value;
	post["js"] = document.querySelector("#js").value;
	post["use_theme_css"] = document.querySelector("#use_theme_css").value;
	post["use_theme_js"] = document.querySelector("#use_theme_js").value;
	post["thumbnail"] = document.querySelector("#thumbnail").value;
	post["categories"] = document.querySelector("#categories").value;
	post["tags"] = document.querySelector("#tags").value;
	post["post_status"] = document.querySelector("#post_status").value;
	return post;
}

function savePost(values) {
	fetch('/api/post', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'authorization': document.cookie
			.split(';')
		  	.find(row => row.trim().startsWith('sloth_session'))
		  	.split('=')[1]
		},
		body: JSON.stringify(values)
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

function createCategory() {
	fetch('/api/taxonomy/category/new', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'authorization': document.cookie
			.split(';')
		  	.find(row => row.trim().startsWith('sloth_session'))
		  	.split('=')[1]
		},
		body: JSON.stringify({
			categoryName: document.querySelector("#new-category").value,
			slug: document.querySelector("#new-category").value.trim().replace(/\s+/g, '-'),
			postType: document.querySelector("#uuid").dataset["posttypeUuid"],
			post: document.querySelector("#uuid").dataset["uuid"]
		})
	})
		.then(response => {
			console.log(response);
			return response.json()
		})
		.then(data => {
			console.log('Success:', data);
			const categories = document.querySelector("#categories");
			while (categories.lastElementChild) {
				categories.removeChild(categories.lastElementChild);
		  	}
		  	console.log(data);
		})
		.catch((error) => {
			console.error('Error:', error);
		});
}