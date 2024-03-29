let images = [];

document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelector("#open-modal").addEventListener('click', openMediaUploadModal);

    const deleteButtons = document.querySelectorAll(".delete-button");
    for (const button of deleteButtons) {
        button.addEventListener('click', deleteButton)
    }
    document.querySelector("media-uploader").addEventListener('uploaded', (event) => {
        console.log(event);
        renderImages(Object.values(event.detail));
    })

    document.querySelector("remove-media-modal").addEventListener('deleted', (event) => {
        renderImages(Object.values(event.detail));
    })
});

function openMediaUploadModal() {
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
    const dialog = document.querySelector("remove-media-modal");
    dialog.open(event.target.dataset["filePath"], event.target.dataset["alt"], event.target.dataset["uuid"]);
}