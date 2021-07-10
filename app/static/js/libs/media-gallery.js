class MediaGallery extends HTMLElement {
    #shadow = null;

    constructor() {
        super();
        this.#shadow = this.attachShadow({mode: 'closed'});
        this.#language = this.getAttribute("language");
        if (!this.getAttribute("in-post-editor")) {
            this.#renderImages();
        }
    }

    openModal() {
        if (!this.getAttribute("in-post-editor")) {
            return;
        }
        const dialog = document.createElement("dialog");
        this.#shadow.appendChild(dialog);
        const closeButton = document.createElement("button");
        closeButton.textContent = "Close";
        closeButton.addEventListener('click', this.#closeModal);
    }

    #closeModal() {
        this.#shadow.querySelector("dialog")?.removeAttribute("open")
        this.#shadow.removeChild(this.#shadow.querySelector("dialog"));
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