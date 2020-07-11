let images = [];

document.addEventListener('DOMContentLoaded', (event) => {
    // 1. open upload modal

    document.querySelector("#open-modal").addEventListener('click', openModal);

    // 2. upload file


    // 3. delete file query
});

function openModal() {
    const dialog = document.querySelector("#modal");
    dialog.setAttribute('open', '');

    const fileLabel = document.createElement('label');
    fileLabel.setAttribute('for', 'file-upload');
    fileLabel.textContent = "File";
    dialog.appendChild(fileLabel);

    const fileUploadInput = document.createElement('input');
    fileUploadInput.setAttribute('id', 'file-upload');
    fileUploadInput.setAttribute("type", "file");
    dialog.appendChild(fileUploadInput);

    const altLabel = document.createElement('label');
    altLabel.setAttribute('for', 'alt');
    altLabel.textContent = "Alternative text";
    dialog.appendChild(altLabel);

    const altInput = document.createElement('input');
    altInput.setAttribute('id', 'alt');
    altInput.setAttribute("type", "text");
    dialog.appendChild(altInput);

    const uploadButton = document.createElement('button');
    uploadButton.textContent = "Upload file";
    uploadButton.addEventListener('click', () => {
        uploadFile();
        closeModal(dialog);
    });
    dialog.appendChild(uploadButton);


    const closeButton = document.createElement('button');
    closeButton.textContent = 'Close'
    closeButton.addEventListener('click', () => closeModal(dialog));
    dialog.appendChild(closeButton);
}

function closeModal(dialog) {
    while (dialog.firstChild) {
        dialog.removeChild(dialog.lastChild);
    }
    dialog.removeAttribute('open');
}

function renderImages() {

}

function uploadFile() {
    const formData = new FormData();
    const fileField = document.querySelector('#file-upload');
    const altField = document.querySelector("#alt")

    formData.append('alt', altField.value);
    formData.append('image', fileField.files[0]);

    fetch('/api/media/upload-file', {
        method: 'POST',
        headers: {
			'authorization': document.cookie
			.split(';')
		  	.find(row => row.trim().startsWith('sloth_session'))
		  	.split('=')[1]
		},
        body: formData
    }).then(response => response.json()).then(result => {
        console.log('Success:', result);
    }).catch(error => {
        console.error('Error:', error);
    });
}