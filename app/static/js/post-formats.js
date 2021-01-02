document.addEventListener('DOMContentLoaded', function() {
    document.querySelector("#create-new-post-format").addEventListener('click', addPostFormat);
    document.querySelectorAll(".edit-button").forEach(button => {
        button.addEventListener('click', editRow)
    })

});

function addPostFormat() {
    const formatFormTemplate = document.querySelector("#format-form");
    const formatForm = formatFormTemplate.content.cloneNode(true);
    const saveButton = formatForm.querySelector(".save-button");
    saveButton.addEventListener('click', saveFormat);
    saveButton.setAttribute('data-uuid', 'new');
    const cancelButton = formatForm.querySelector(".cancel-button");
    cancelButton.addEventListener('click', cancelAddingFormat);
    formatForm.querySelector("br").classList.add("hidden");
    formatForm.querySelector(".delete-button").classList.add("hidden");
    document.querySelector("table tbody").appendChild(formatForm);
}

function editRow(event) {
    const formatFormTemplate = document.querySelector("#format-form");
    const formatForm = formatFormTemplate.content.cloneNode(true);

    formatForm.querySelector(".display-name input").value = event.target.parentNode.parentNode.querySelector(".display-name").textContent
    formatForm.querySelector(".slug input").value = event.target.parentNode.parentNode.querySelector(".slug").textContent

    const saveButton = formatForm.querySelector(".save-button");
    saveButton.addEventListener('click', saveFormat);
    saveButton.setAttribute('data-uuid', event.target.dataset["uuid"]);
    saveButton.setAttribute('data-deletable', event.target.dataset["deletable"]);
    const cancelButton = formatForm.querySelector(".cancel-button");
    cancelButton.addEventListener('click', cancelAddingFormat);
    if (event.target.dataset["deletable"] === 'False') {
        formatForm.querySelector("br").classList.add("hidden");
        formatForm.querySelector(".delete-button").classList.add("hidden");
    } else {
        formatForm.querySelector(".delete-button").addEventListener('click', deleteFormat);
        formatForm.querySelector(".delete-button").setAttribute('data-uuid', event.target.dataset["uuid"]);
    }

    event.target.parentNode.parentNode.parentNode.replaceChild(formatForm, event.target.parentNode.parentNode)
}

function saveFormat(event) {
    fetch('/api/post/formats', {
        method: 'POST',
        headers: {
            'authorization': document.cookie
                .split(';')
                .find(row => row.trim().startsWith('sloth_session'))
                .split('=')[1],
        },
        body: JSON.stringify({
            post_type_uuid: postTypeUuid,
            display_name: event.target.parentNode.parentNode.querySelector(".display-name input").value,
            slug: event.target.parentNode.parentNode.querySelector(".slug input").value,
            uuid: event.target.dataset["uuid"]
        })
    }).then(response => {
        if (response.ok) {
            return response.json()
        }
        throw `${response.status}: ${response.statusText}`
    }).then(data => {
        event.target.parentNode.parentNode.querySelector(".display-name").textContent = data["display_name"];
        event.target.parentNode.parentNode.querySelector(".slug").textContent = data["slug"];
        const editButton = document.createElement("button");
        editButton.setAttribute('data-uuid', data["uuid"]);
        editButton.setAttribute('data-deletable', data["deletable"]);
        editButton.textContent = "Edit";
        editButton.addEventListener('click', editRow);
        const actionTd = event.target.parentNode;
        while (actionTd.firstChild) {
            actionTd.removeChild(
                actionTd.lastChild
            );
        }
        actionTd.appendChild(editButton);
    }).catch((error) => {
        console.error('Error:', error);
    });
}

function cancelAddingFormat(event) {
    if (event.target.parentNode.querySelector(".save-button").dataset["uuid"] === 'new') {
        event.target.parentNode.parentNode.parentNode.removeChild(event.target.parentNode.parentNode)
    } else {
        event.target.parentNode.parentNode.querySelector(".display-name").textContent = event.target.parentNode.parentNode.querySelector(".display-name input").value;
        event.target.parentNode.parentNode.querySelector(".slug").textContent = event.target.parentNode.parentNode.querySelector(".slug input").value;
        const editButton = document.createElement("button");
        editButton.setAttribute('data-uuid', event.target.dataset["uuid"]);
        editButton.setAttribute('data-deletable', event.target.dataset["deletable"]);
        editButton.textContent = "Edit";
        const actionTd = event.target.parentNode;
        while (actionTd.firstChild) {
            actionTd.removeChild(
                actionTd.lastChild
            );
        }
        actionTd.appendChild(editButton);

    }
}

function deleteFormat(event) {
    fetch('/api/post/formats', {
        method: 'DELETE',
        headers: {
            'authorization': document.cookie
                .split(';')
                .find(row => row.trim().startsWith('sloth_session'))
                .split('=')[1],
        },
        body: JSON.stringify({
            uuid: event.target.dataset["uuid"]
        })
    }).then(response => {
        if (response.ok) {
            return response.json()
        }
        throw `${response.status}: ${response.statusText}`
    }).then(data => {
        event.target.parentNode.parentNode.parentNode.removeChild(event.target.parentNode.parentNode)
    }).catch((error) => {
        console.error('Error:', error);
    });
}
