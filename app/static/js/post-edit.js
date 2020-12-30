const post = {};

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
    fetch(`/api/post/media/${currentLanguage}`, {
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
            if (response.ok) {
                return response.json()
            }
            throw `${response.status}: ${response.statusText}`
        })
        .then(data => {
            gallery.images = data.media;
        })
        .catch((error) => {
            console.error('Error:', error);
        });

    document.querySelector("#gallery-opener").addEventListener('click', () => {
        openGalleryDialog(gallery.images, "gallery");
    });

    document.querySelector("#pick-thumbnail").addEventListener('click', () => {
        openGalleryDialog(gallery.images, "thumbnail");
    })

    // 2. publish post button
    document.querySelector("#publish-button")?.addEventListener('click', publishPost);
    document.querySelector("#publish-create")?.addEventListener('click', publishPostCreate);

    // 3. save draft button
    document.querySelector("#save-draft")?.addEventListener('click', saveDraft);
    document.querySelector("#save-create")?.addEventListener('click', saveDraftCreate);

    // 4. update button
    document.querySelector("#update-button")?.addEventListener('click', updatePost);
    document.querySelector("#update-create")?.addEventListener('click', updatePostCreate)

    // 5. schedule button
    document.querySelector("#schedule-button")?.addEventListener('click', schedulePost);

    document.querySelector("#title").addEventListener('blur', (event) => {
        document.querySelector("#slug").value = event.target?.value
            .trim()
            .toLocaleLowerCase()
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[\u00DF]/g, "ss")
            .replace(/[^a-zA-Z0-9\-]+/g, "");
    });

    document.querySelector("#create-category")?.addEventListener('click', createCategory);

    document.querySelector("#delete-button")?.addEventListener('click', deletePost);

    //document.querySelector("#weird-button").addEventListener('click', replaceSelectionWithHtml);
    document.querySelector("#post_status").addEventListener('change', postStatusChanged);

    document.querySelector("#add-tags")?.addEventListener('click', addTags);
    document.querySelectorAll(".delete-tag").forEach(button => {
        button.addEventListener('click', deleteTag)
    });
});

function openGalleryDialog(data, type) {
    const dialog = document.querySelector("#modal");
    dialog.setAttribute('open', '');
    const copyResult = document.createElement('p');
    dialog.appendChild(copyResult);
    const mediaSection = document.createElement('section')
    gallery.images.forEach((item) => {
        const wrapper = document.createElement('article');
        wrapper.setAttribute('style', "width: 100px; height: 100px;");
        // uuid, file_path, alt
        const image = document.createElement('img');
        image.setAttribute('src', item['filePath']);
        image.setAttribute('alt', item["alt"]);
        image.setAttribute("loading", "lazy");
        image.setAttribute('style', "max-width: 100%; max-height: calc(100% - 2rem);");
        wrapper.appendChild(image);

        const actionButton = document.createElement('button');
        switch (type) {
            case "gallery":
                actionButton.textContent = 'Copy URL'
                actionButton.addEventListener('click', () => {
                    copyResult.textContent = '';
                    navigator.clipboard.writeText(`<img src="${item['filePath']}" alt="${item['alt']}" />`).then(function () {
                        /* clipboard successfully set */
                        copyResult.textContent = 'URL copied to clipboard';
                    }, function () {
                        /* clipboard write failed */
                        copyResult.textContent = 'Error copying URL to clipboard';
                    });
                });
                break;
            case "thumbnail":
                actionButton.textContent = 'Choose'
                actionButton.addEventListener('click', () => {
                    const thumbnailInput = document.querySelector("#thumbnail");
                    thumbnailInput.setAttribute('value', item["uuid"])
                    const thumbnailWrapper = document.querySelector("#thumbnail-wrapper");
                    while (thumbnailWrapper.lastChild) {
                        thumbnailWrapper.removeChild(thumbnailWrapper.lastChild)
                    }
                    const image = document.createElement('img');
                    image.setAttribute('src', item['filePath']);
                    image.setAttribute('alt', item['alt']);
                    thumbnailWrapper.appendChild(image);
                    dialog.close();
                });
                break;
        }
        wrapper.appendChild(actionButton);

        mediaSection.appendChild(wrapper);
    });
    dialog.appendChild(mediaSection);
    const closeButton = document.createElement('button');
    closeButton.textContent = 'Close'
    closeButton.addEventListener('click', () => {
        while (dialog.firstChild) {
            dialog.removeChild(dialog.lastChild);
        }
        dialog.removeAttribute('open');
    });
    dialog.appendChild(closeButton);
}

function publishPost() {
    const values = collectValues();
    if (!values) {
        return;
    }
    values["post_status"] = "published";
    console.log(values);
    savePost(values);
}

function publishPostCreate() {
    const values = collectValues();
    if (!values) {
        return;
    }
    values["post_status"] = "published";
    values["createTranslation"] = document.querySelector("#create-lang").value.length > 0 ? document.querySelector("#create-lang").value : null;
    console.log(values);
    saveCreatePost(values);
}

function schedulePost() {
    const values = collectValues();
    if (!values) {
        return;
    }
    values["post_status"] = "scheduled";
    savePost(values);
}

function saveDraft() {
    const values = collectValues();
    if (!values) {
        return;
    }
    values["post_status"] = "draft";
    savePost(values);
}

function saveDraftCreate() {
    const values = collectValues();
    if (!values) {
        return;
    }
    values["createTranslation"] = document.querySelector("#create-lang").value.length > 0 ?
        document.querySelector("#create-lang").value : null;
    values["post_status"] = "draft";
    savePost(values);
}

function updatePost() {
    const values = collectValues();
    if (!values) {
        return;
    }
    savePost(values);
}

function updatePostCreate() {
    const values = collectValues();
    if (!values) {
        return;
    }
    values["createTranslation"] = document.querySelector("#create-lang").value.length > 0 ?
        document.querySelector("#create-lang").value : null;
    saveCreatePost(values);
}

function collectValues() {
    const post = {};
    post["uuid"] = document.querySelector("#uuid").dataset["uuid"];
    post["post_type_uuid"] = document.querySelector("#uuid").dataset["posttypeUuid"];
    post["new"] = document.querySelector("#uuid").dataset["new"];
    post["original_post"] = document.querySelector("#uuid").dataset["originalPost"];
    post["title"] = document.querySelector("#title").value;
    if (post["title"].length === 0) {
        return false;
    }
    post["slug"] = document.querySelector("#slug").value;
    post["excerpt"] = document.querySelector("#excerpt").value;
    post["content"] = document.querySelector("#content").value;
    post["css"] = document.querySelector("#css").value;
    post["js"] = document.querySelector("#js").value;
    post["use_theme_css"] = document.querySelector("#use_theme_css").checked;
    post["use_theme_js"] = document.querySelector("#use_theme_js").checked;
    post["thumbnail"] = document.querySelector("#thumbnail").value;
    post["publish_date"] = (new Date(`${document.querySelector("#publish_date").value}T${document.querySelector("#publish_time").value}`)).getTime();
    post["categories"] = [];
    for (const option of document.querySelector("#categories").selectedOptions) {
        post["categories"].push(option.value);
    }
    post["tags"] = [];
    for (const node of document.querySelector("#tags-div").childNodes) {
        if (!node.dataset) {
            continue;
        }
        post["tags"].push({
            uuid: node.dataset["uuid"],
            slug: node.dataset["slug"],
            displayName: node.dataset["displayName"]
        })
    }
    post["post_status"] = document.querySelector("#post_status").value;
    if (post["post_status"] === "protected") {
        post["password"] = document.querySelector("#password_protection").value;
    }
    post["approved"] = document.querySelector("#import_approved") ? document.querySelector("#import_approved").checked : false;
    post["lang"] = currentLanguage;
    return post;
}

function savePost(values) {
    const metadataButtons = document.querySelectorAll(".metadata button");
    metadataButtons.forEach(button => {
        button.setAttribute("disabled", "true");
    });
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
            if (response.ok) {
                return response.json()
            }
            throw `${response.status}: ${response.statusText}`
        })
        .then(data => {
            if (window.location.pathname.indexOf("/new/") >= 0) {
                window.location.replace(`/${window.location.pathname.substring(1).split("/")[0]}/${data.uuid}/edit`);
            } else {
                metadataButtons.forEach(button => button.removeAttribute("disabled"));
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function saveCreatePost(values) {
    const metadataButtons = document.querySelectorAll(".metadata button");
    metadataButtons.forEach(button => {
        button.setAttribute("disabled", "true");
    });
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
            if (response.ok) {
                return response.json()
            }
            throw `${response.status}: ${response.statusText}`
        })
        .then(data => {
            window.location.replace(
                `/${window.location.pathname.substring(1).split("/")[0]}/${data["postType"]}/new/${values["createTranslation"]}?original=${values['uuid']}`
            );
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
            slug: document.querySelector("#new-category").value
                .trim()
                .toLocaleLowerCase()
                .replace(/\s+/g, '-')
                .replace(/-+/g, '-')
                .normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "")
                .replace(/[\u00DF]/g, "ss")
                .replace(/[^a-zA-Z0-9\-]+/g, ""),
            postType: document.querySelector("#uuid").dataset["posttypeUuid"],
            post: document.querySelector("#uuid").dataset["uuid"],
            lang: currentLanguage
        })
    })
        .then(response => {
            if (response.ok) {
                return response.json()
            }
            throw `${response.status}: ${response.statusText}`
        })
        .then(data => {
            console.log('Success:', data);
            const categories = document.querySelector("#categories");
            while (categories.lastElementChild) {
                categories.removeChild(categories.lastElementChild);
            }
            for (const category of data) {
                const option = document.createElement("option");
                option.setAttribute("value", category["uuid"]);
                option.textContent = category["display_name"];
                if (category["selected"]) {
                    option.setAttribute("selected", "selected");
                }
                categories.appendChild(option);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function deletePost() {
    fetch('/api/post/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'authorization': document.cookie
                .split(';')
                .find(row => row.trim().startsWith('sloth_session'))
                .split('=')[1]
        },
        body: JSON.stringify({
            post: document.querySelector("#uuid").dataset["uuid"]
        })
    })
        .then(response => {
            if (response.ok) {
                return response.json()
            }
            throw `${response.status}: ${response.statusText}`
        })
        .then(data => {
            console.log('Success:', data);
            window.location.replace(`${window.location.origin}/post/${data["post_type"]}`);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function postStatusChanged(event) {
    if (event.target.value === "protected") {
        document.querySelector("#password_protection_label").classList.remove("hidden");
        document.querySelector("#password_protection").classList.remove("hidden");
    } else {
        document.querySelector("#password_protection_label").classList.add("hidden");
        document.querySelector("#password_protection").classList.add("hidden");
    }
}

function addTags(event) {
    const newTags = document.querySelector("#tags-input")?.value.split(",");
    document.querySelector("#tags-input").value = "";
    const nodes = [];
    for (const tag of newTags) {
        let canBeAdded = true;
        const tagSlug = tag.trim()
            .toLocaleLowerCase()
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .replace(/[^a-zA-Z0-9\-]+/g, "");
        /* refactoring candidate */
        for (const node of document.querySelector("#tags-div").childNodes) {
            if (node.dataset?.slug === tagSlug) {
                canBeAdded = false;
            }
        }
        for (const node of nodes) {
            if (node.dataset?.slug === tagSlug) {
                canBeAdded = false;
            }
        }
        if (canBeAdded) {
            const span = document.createElement('span');
            span.setAttribute("data-uuid", "added");
            span.setAttribute("data-slug", tagSlug);
            span.setAttribute("data-display-name", tag.trim());
            span.textContent = tag.trim();

            const deleteTagButton = document.createElement('button');
            deleteTagButton.setAttribute("class", "delete-tag");
            deleteTagButton.addEventListener('click', deleteTag);
            deleteTagButton.textContent = "🚮";

            span.append(deleteTagButton);
            nodes.push(span);
        }
    }
    document.querySelector("#tags-div").append(...nodes);
}

function deleteTag(event) {
    event.target.parentNode.parentNode.removeChild(event.target.parentNode)
}

function getSelectionHtml() {
    debugger;
    var html = "";
    if (typeof window.getSelection != "undefined") {
        var sel = window.getSelection();
        if (sel.rangeCount) {
            var container = document.createElement("div");
            for (var i = 0, len = sel.rangeCount; i < len; ++i) {
                container.appendChild(sel.getRangeAt(i).cloneContents());
            }
            html = container.innerHTML;
        }
    } else if (typeof document.selection != "undefined") {
        if (document.selection.type == "Text") {
            html = document.selection.createRange().htmlText;
        }
    }
    alert(html);
}

function replaceSelectionWithHtml(html) {
    var range;
    if (window.getSelection && window.getSelection().getRangeAt) {
        debugger;
        range = window.getSelection().getRangeAt(0);
        const insideRange = range.extractContents();
        const div = document.createElement("div");
        div.appendChild(insideRange)
        range.insertNode(div);
    } else if (document.selection && document.selection.createRange) {
        range = document.selection.createRange();
        range.pasteHTML(html);
    }
}