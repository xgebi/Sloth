let images = [];

document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelector("#open-modal").addEventListener('click', openModal);

    const deleteButtons = document.querySelectorAll(".delete-button");
    for (const button of deleteButtons) {
        button.addEventListener('click', deleteButton)
    }
    document.querySelector("media-uploader").addEventListener('uploaded', (event) => {
        console.log(event);
        renderImages(Object.values(event.detail));
    })
});

function openModal() {
    const mediaUploader = document.querySelector("media-uploader");
    mediaUploader.languages = languages;
    mediaUploader.open();
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
        for (const alt of medium.alts) {
            const p = document.createElement("p");
            p.textContent = `Alt (${alt['lang']}): ${alt["alt"]}`;
            article.appendChild(p)
        }
        const deleteButton = document.createElement('button');
        deleteButton.setAttribute("class", "delete-button");
        deleteButton.setAttribute("data-uuid", medium["uuid"]);
        deleteButton.setAttribute("data-file-path", medium["file_url"]);
        deleteButton.textContent = "Delete"
        article.appendChild(deleteButton);
        gallery.appendChild(article);
    }
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