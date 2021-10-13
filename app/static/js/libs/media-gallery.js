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

        const linkElem = document.createElement('link');
        linkElem.setAttribute('rel', 'stylesheet');
        linkElem.setAttribute('href', '/static/css/media-gallery.css');
        // Attach the created element to the shadow dom
        this.#shadow.appendChild(linkElem);

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
        if (dialog.querySelector('.images')) {
            dialog.removeChild(dialog.querySelector('.images'));
        }
        if (dialog.querySelector('.pagination')) {
            dialog.removeChild(dialog.querySelector('.pagination'));
        }
        const numberOfPages = Math.ceil(this.#listOfMedia.length / this.#pageSize);
        const slice = this.#listOfMedia.slice(this.#pageSize * (this.#currentPage), this.#pageSize * (this.#currentPage + 1));

        const imagesWrapper = document.createElement('div');
        imagesWrapper.setAttribute('class', 'images');

        for (let i = 0; i < slice.length; i++) {
            const figure = document.createElement('figure');
            const img = document.createElement('img');
            img.setAttribute('src', slice[i]['file_url']);
            img.setAttribute('alt', slice[i]['alts'].filter(alt => alt.lang_uuid === currentLanguage)[0].alt);
            figure.appendChild(img);

            const select = document.createElement('button');
            select.textContent = 'Select';
            figure.appendChild(select);
            imagesWrapper.appendChild(figure);
        }

        dialog.appendChild(imagesWrapper);

        const paginationWrapper = document.createElement('div');
        paginationWrapper.setAttribute('class', 'pagination')
        const firstButton = document.createElement('button');
        firstButton.textContent = '1';
        firstButton.addEventListener('click', () => {
            this.#currentPage = 0;
            this.#displayMedia(dialog);
        });
        paginationWrapper.appendChild(firstButton);

        if (this.#currentPage > 1) {
            const previousButton = document.createElement('button');
            previousButton.textContent = (this.#currentPage).toString();
            paginationWrapper.appendChild(previousButton);
            previousButton.addEventListener('click', () => {
                this.#currentPage -= 1;
                this.#displayMedia(dialog);
            });
        }
        if (this.#currentPage !== 0 && this.#currentPage !== numberOfPages - 1) {
            const currentPageSpan = document.createElement('span');
            currentPageSpan.textContent = (this.#currentPage + 1).toString();
            paginationWrapper.appendChild(currentPageSpan);
        }

        if (this.#currentPage < numberOfPages - 2) {
            const nextButton = document.createElement('button');
            nextButton.textContent = (this.#currentPage + 2).toString();
            paginationWrapper.appendChild(nextButton);
            nextButton.addEventListener('click', () => {
                this.#currentPage += 1;
                this.#displayMedia(dialog);
            });
        }

        const lastButton = document.createElement('button');
        lastButton.textContent = numberOfPages.toString();
        paginationWrapper.appendChild(lastButton);
        lastButton.addEventListener('click', () => {
            this.#currentPage = numberOfPages - 1;
            this.#displayMedia(dialog);
        });
        dialog.appendChild(paginationWrapper);
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