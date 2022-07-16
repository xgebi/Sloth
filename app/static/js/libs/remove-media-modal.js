class RemoveMediaModal extends HTMLElement {
    #languages = []
    #shadow = {}

    constructor() {
        super();
        this.#shadow = this.attachShadow({mode: 'open'});
        const linkElem = document.createElement('link');
        linkElem.setAttribute('rel', 'stylesheet');
        linkElem.setAttribute('href', '/static/css/remove-media-modal.css');

        // Attach the created element to the shadow dom
        this.#shadow.appendChild(linkElem);
    }

    open(filePath, alt, uuid) {
        let dialog = this.#shadow.querySelector("dialog");
        if (!dialog) {
            dialog = document.createElement("dialog");
        } else {
            while (dialog.lastElementChild) {
                dialog.removeChild(dialog.lastElementChild);
            }
        }
        if (dialog?.getAttribute("open")) {
            return;
        }

        const image = document.createElement("img");
        image.setAttribute("src", filePath);
        image.setAttribute("alt", alt);
        dialog.appendChild(image);

        const deleteButton = document.createElement('button');
        deleteButton.textContent = "Delete image";
        deleteButton.setAttribute('id', 'close-button');
        deleteButton.addEventListener('click', () => {
            this.#deleteFile(uuid)
        });
        dialog.appendChild(deleteButton);

        const closeButton = document.createElement('button');
        closeButton.textContent = "Close dialog";
        closeButton.setAttribute('id', 'close-button');
        closeButton.addEventListener('click', () => {
            this.#close(dialog);
        });
        dialog.appendChild(closeButton);

        this.#shadow.appendChild(dialog);
        dialog.showModal();
    }

    #close() {
        this.#shadow.querySelector("dialog").close();
    }

    #deleteFile(uuid) {
        fetch('/api/media/delete-file', {
            method: 'DELETE',
            headers: {
                'authorization': document.cookie
                    .split(';')
                    .find(row => row.trim().startsWith('sloth_session'))
                    .split('=')[1]
            },
            body: JSON.stringify({
                uuid: uuid,
            })
        }).then(response => {
            if (response.ok) {
                return response.json()
            }
            throw `${response.status}: ${response.statusText}`
        }).then(result => {
            this.dispatchEvent(new CustomEvent('deleted', {
                detail: result["media"]
            }));
            this.#shadow.querySelector("dialog").close();
        }).catch(error => {
            console.error('Error:', error);
        });
    }
}

customElements.define('remove-media-modal', RemoveMediaModal);