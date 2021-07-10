class MediaUploader extends HTMLElement {
    #languages = []
    #shadow = {}

    constructor() {
        super();
        this.#shadow = this.attachShadow({mode: 'closed'});
        const linkElem = document.createElement('link');
        linkElem.setAttribute('rel', 'stylesheet');
        linkElem.setAttribute('href', '/static/css/media-uploader.css');

        // Attach the created element to the shadow dom
        this.#shadow.appendChild(linkElem);
    }

    open() {
        let dialog = this.#shadow.querySelector("dialog");
        if (dialog?.getAttribute("open")) {
            return;
        }

        dialog = document.createElement("dialog");

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

        this.#languages.forEach(lang => {
            const altLabel = document.createElement('label');
            altLabel.setAttribute('for', `alt-${lang["long_name"].toLowerCase()}`);
            altLabel.textContent = `Alternative text (${lang["long_name"]})`;
            dialog.appendChild(altLabel);

            const altInput = document.createElement('input');
            altInput.setAttribute('id', `alt-${lang["long_name"].toLowerCase()}`);
            altInput.setAttribute("class", "alt-input");
            altInput.setAttribute("type", "text");
            altInput.setAttribute("data-lang", lang["uuid"]);

            dialog.appendChild(altInput);
        })

        const uploadButton = document.createElement('button');
        uploadButton.textContent = "Upload file";
        uploadButton.addEventListener('click', () => {
            this.#uploadFile();
            this.#close(dialog);
        });
        dialog.appendChild(uploadButton);

        const closeButton = document.createElement('button');
        closeButton.textContent = "Close dialog";
        closeButton.addEventListener('click', () => {
            this.#close(dialog);
        });
        dialog.appendChild(closeButton);

        this.#shadow.appendChild(dialog);
        dialog.showModal();
    }

    set languages(languages) {
        this.#languages = languages;
    }

    #close() {
        const dialog = this.#shadow.querySelector("dialog");
        dialog.removeAttribute("open");
        this.#shadow.removeChild(dialog);

    }

    #uploadFile() {
        const formData = new FormData();
        const fileField = this.#shadow.querySelector('#file-upload');
        const altFields = this.#shadow.querySelectorAll(".alt-input");

        const alts = [];
        altFields.forEach(alt => {
            alts.push({
                lang_uuid: alt.dataset["lang"],
                text: alt.value
            })
        });

        formData.append('alt', JSON.stringify(alts));
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
            this.dispatchEvent(new CustomEvent('uploaded', {
                detail: result["media"]
            }));
        }).catch(error => {
            console.error('Error:', error);
        });
    }
}

customElements.define('media-uploader', MediaUploader);