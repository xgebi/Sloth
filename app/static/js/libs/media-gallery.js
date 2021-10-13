class MediaGallery extends HTMLElement {
    #shadow = null;
    #language = null;
    #listOfMedia = null;
    #currentPage = 0;
    #pageSize = 12;

    constructor() {
        super();
        this.#shadow = this.attachShadow({mode: 'closed'});
        this.#language = this.getAttribute("language");
        if (!this.getAttribute("in-post-editor")) {
            this.#renderImages();
        }
    }

    openModal(listOfMedia, isThumbnail = false) {
        if (!this.getAttribute("in-post-editor")) {
            return;
        }
        this.#listOfMedia = listOfMedia;
        let dialog;
        if (!this.#shadow.querySelector('dialog')) {
            dialog = document.createElement("dialog");
            dialog.setAttribute('style', 'height: 100px; width: 100px; background: red;');
            this.#shadow.appendChild(dialog);
            dialog.showModal();
            const closeButton = document.createElement("button");
            closeButton.textContent = "Close";
            closeButton.addEventListener('click', this.#closeModal);
            dialog.appendChild(closeButton);
        } else {
            dialog = this.#shadow.querySelector('dialog').showModal();
        }
        this.#displayMedia(dialog);
    }

    #displayMedia(dialog) {
        const slice = this.#listOfMedia[this.#pageSize * (this.#currentPage - 1), this.#pageSize * (this.#currentPage + 1)];
    }

    #closeModal() {
        this.parentElement.close();
        const shadow = this.parentElement.parentElement;
    }

    #renderImages() {
        let container = document.createElement("div");



        if (this.#shadow.querySelector("dialog")) {
            this.#shadow.querySelector("dialog")?.appendChild(container);
            this.#shadow.querySelector("dialog")?.getAttribute("open")
        } else {
            this.#shadow.appendChild(container);
        }

    }

    #openDetail() {

    }

    #saveDetail() {

    }

    #deleteImage() {

    }

    #pickMedia() {
        this.dispatchEvent(new CustomEvent('picked', { detail: { image: "" } }));
        this.#closeModal();
    }
}

customElements.define('media-gallery', MediaGallery);