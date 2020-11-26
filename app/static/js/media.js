let images = [];

document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelector("#open-modal").addEventListener('click', openModal);

    const deleteButtons = document.querySelectorAll(".delete-button");
    for (const button of deleteButtons) {
        button.addEventListener('click', deleteButton)
    }
});

function openModal() {
    const dialog = document.querySelector("#modal");
    if (dialog.getAttribute("open")) {
        return;
    }
    dialog.showModal();

    const fileLabel = document.createElement('label');
    fileLabel.setAttribute('for', 'file-upload');
    fileLabel.textContent = "File";
    dialog.appendChild(fileLabel);

    const fileUploadInput = document.createElement('input');
    fileUploadInput.setAttribute('id', 'file-upload');
    fileUploadInput.setAttribute("type", "file");
    dialog.appendChild(fileUploadInput);

    const h2 = document.createElement('h2');
    h2.textContent = "Alt descriptions";
    dialog.appendChild(h2)

    languages.forEach(lang => {
        const altLabel = document.createElement('label');
        altLabel.setAttribute('for', 'alt');
        altLabel.textContent = "Alternative text";
        dialog.appendChild(altLabel);

        const altInput = document.createElement('input');
        altInput.setAttribute('id', 'alt');
        altInput.setAttribute("type", "text");
        dialog.appendChild(altInput);
    })

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

function renderImages(media) {
    const gallery = document.querySelector("#media-gallery");
    while (gallery.firstChild) {
        gallery.removeChild(gallery.lastChild);
    }

    for (const medium of media) {
        const article = document.createElement('article');
        const image = document.createElement("img");
        image.setAttribute("src", medium["file_url"]);
        image.setAttribute("alt", medium["alt"]);
        article.appendChild(image)
        const p = document.createElement("p");
        p.textContent = `Alt: ${medium["alt"]}`;
        article.appendChild(p)
        const deleteButton = document.createElement('button');
        deleteButton.setAttribute("class", "delete-button");
        deleteButton.setAttribute("data-uuid", medium["uuid"]);
        deleteButton.setAttribute("data-file-path", medium["file_url"]);
        deleteButton.textContent = "Delete"
        article.appendChild(deleteButton);
        gallery.appendChild(article);
    }
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
    }).then(response => {
        if (response.ok) {
            return response.json()
        }
        throw `${response.status}: ${response.statusText}`
    }).then(result => {
        renderImages(result["media"]);
    }).catch(error => {
        console.error('Error:', error);
    });
}

function deleteButton(event) {
    const dialog = document.querySelector("#modal");
    dialog.showModal();

    const image = document.createElement("img");
    image.setAttribute("src", event.target.dataset["filePath"]);
    dialog.appendChild(image);


    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Delete file'
    deleteButton.addEventListener('click', () => {
        closeModal(dialog);
        fetch('/api/media/delete-file', {
            method: 'DELETE',
            headers: {
                'authorization': document.cookie
                    .split(';')
                    .find(row => row.trim().startsWith('sloth_session'))
                    .split('=')[1]
            },
            body: JSON.stringify({uuid: event.target.dataset["uuid"]})
        }).then(response => {
            if (response.ok) {
                return response.json()
            }
            throw `${response.status}: ${response.statusText}`
        }).then(result => {
            renderImages(result["media"]);
        }).catch(error => {
            console.error('Error:', error);
        });
    });
    dialog.appendChild(deleteButton);

    const closeButton = document.createElement('button');
    closeButton.textContent = 'Keep file'
    closeButton.addEventListener('click', () => closeModal(dialog));
    dialog.appendChild(closeButton);
}