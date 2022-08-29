const post = {};

// not ideal but it'll do for now
const META_DESC = 160;
const SOCIAL_DESC = 200;

document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelector("media-gallery").addEventListener('thumbnail-picked', (ev) => {
        console.log(ev.detail);
        const thumbnailWrapper = document.querySelector('#thumbnail-wrapper');
        while (thumbnailWrapper.lastElementChild) {
            thumbnailWrapper.removeChild(thumbnailWrapper.lastElementChild);
        }
        const thumbnailImg = document.createElement('img');
        thumbnailImg.setAttribute('src', ev.detail.image);
        thumbnailImg.setAttribute('alt', ev.detail.alt);
        document.querySelector('#thumbnail').setAttribute('value', ev.detail.uuid);
    });
    document.querySelector("#gallery-opener").addEventListener('click', () => {
        const mediaGallery = document.querySelector("media-gallery");
        mediaGallery.openModal(listOfMedia);
    });

    document.querySelector("#pick-thumbnail").addEventListener('click', () => {
        const mediaGallery = document.querySelector("media-gallery");
        mediaGallery.openModal(listOfMedia, true);
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

    document.querySelector("#meta-description").addEventListener('input', calculateLengthEvent);
    calculateLength(META_DESC, "#meta-description");
    document.querySelector("#social-description").addEventListener('input', calculateLengthEvent)
    calculateLength(SOCIAL_DESC, "#social-description");

    document.querySelector("#add-library").addEventListener('click', addLibrary)
    document.querySelectorAll("#library-list button").forEach(button => button.addEventListener('click', removeLibraryFromList));

    const postEditor = document.querySelector("post-editor");
    postEditor.sections = sections;
    const mediaGallery = document.querySelector("media-gallery");
    mediaGallery.addEventListener('picked', (event) => {
        postEditor.addImageToCurrentTextArea(event.detail.image);
    })
});

function calculateLengthEvent(event) {
    if (event.target.id === "meta-description") {
        calculateLength(META_DESC, `#${event.target.id}`);
    } else if (event.target.id === "social-description") {
        calculateLength(SOCIAL_DESC, `#${event.target.id}`);
    }
}

function calculateLength(length, elementIdName) {
    const textAreaLength = document.querySelector(elementIdName).value.length
    const counter = document.querySelector(`${elementIdName}-counter`)
    counter.textContent = `${textAreaLength} / ${length}`
}

function publishPost() {
    const values = collectValues();
    if (!values) {
        return;
    }
    if (values["post_status"] !== "protected") {
        values["post_status"] = "published";
    }
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
    post["original_lang_entry_uuid"] = document.querySelector("#uuid").dataset["originalPost"];
    post["title"] = document.querySelector("#title").value;
    if (post["title"].length === 0) {
        return false;
    }
    post["slug"] = document.querySelector("#slug").value;
    post["sections"] = document.querySelector("post-editor").getSections();
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
    document.querySelectorAll("#post-formats input").forEach(input => {
        if (input.checked) {
            post["post_format"] = input.value;
        }
    });
    post["meta_description"] = document.querySelector("#meta-description").value;
    post["twitter_description"] = document.querySelector("#social-description").value;
    const libraryList = document.querySelector("#library-list");
    const libs = [];
    for (let lib of libraryList.children) {
        libs.push({
            libId: lib.dataset["libId"],
            hook: lib.dataset["hook"]
        });
    }
    post["libs"] = libs;
    post["pinned"] =  document.querySelector("#post-pinned-check").checked;
    return post;
}

function savePost(values) {
    debugger;
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
          if (values["createTranslation"]) {
              let original = values['uuid'];
              if (values['original_lang_entry_uuid']?.length > 0) {
                  original = values['original_lang_entry_uuid'];
              }
              window.location.replace(
                `/${window.location.pathname.substring(1).split("/")[0]}/${data["postType"]}/new/${values["createTranslation"]}?original=${original}`
              );
          } else if (window.location.pathname.indexOf("/new/") >= 0) {
              window.location.replace(`/${window.location.pathname.substring(1).split("/")[0]}/${data.uuid}/edit`);
          } else {
              regenerationCheckInterval = setInterval(checkRegenerationLock, 1000, metadataButtons)
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
            let original = values['uuid'];
            if (values['original_lang_entry_uuid'].length > 0) {
                original = values['original_lang_entry_uuid'];
            }
            window.location.replace(
                `/${window.location.pathname.substring(1).split("/")[0]}/${data["postType"]}/new/${values["createTranslation"]}?original=${original}`
            );
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function createCategory(event) {
    if (document.querySelector("#new-category").value.length === 0) {
        return;
    }
    event.target.setAttribute("disabled", "");
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
            event.target.removeAttribute("disabled", "");
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
            document.querySelector("#new-category").value = "";
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
    } else if (event.target.value === "scheduled") {
        document.querySelector("#publish-button").classList.add("hidden");
        document.querySelector("#schedule-button").classList.remove("hidden");
    } else {
        document.querySelector("#publish-button").classList.remove("hidden");
        document.querySelector("#schedule-button").classList.add("hidden");
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

function addLibrary(event) {
    const select = document.querySelector("#library-select");
    const libraryList = document.querySelector("#library-list");
    if (select.value.length > 0) {
        for (let option of select.options) {
            if (option.value === select.value) {
                for (let libs of libraryList.children) {
                    if (libs.dataset["libId"] === option.value) {
                        return;
                    }
                }
                const span = document.createElement('span');
                span.textContent = option.textContent;
                span.setAttribute("data-lib-id", option.value);
                span.setAttribute("data-hook", document.querySelector("#hook-select").value)
                const button = document.createElement('button');
                button.textContent = "Remove";
                button.addEventListener('click', removeLibraryFromList);
                span.appendChild(button);
                libraryList.appendChild(span);
            }
        }
    }
}

function removeLibraryFromList(event) {
    event.target.parentNode.parentNode.removeChild(event.target.parentNode);
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