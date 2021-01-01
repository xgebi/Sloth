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
    console.log(event.target.parentNode.parentNode, event.target.parentNode.parentNode.parentNode);
    debugger;
    const formatFormTemplate = document.querySelector("#format-form");
    const formatForm = formatFormTemplate.content.cloneNode(true);

    formatForm.querySelector(".display-name input").value = event.target.parentNode.parentNode.querySelector(".display-name").textContent
    formatForm.querySelector(".slug input").value = event.target.parentNode.parentNode.querySelector(".slug").textContent

    const saveButton = formatForm.querySelector(".save-button");
    saveButton.addEventListener('click', saveFormat);
    saveButton.setAttribute('data-uuid', event.target.dataset["uuid"]);
    const cancelButton = formatForm.querySelector(".cancel-button");
    cancelButton.addEventListener('click', cancelAddingFormat);
    if (event.target.dataset["deletable"] === 'False') {
        formatForm.querySelector("br").classList.add("hidden");
        formatForm.querySelector(".delete-button").classList.add("hidden");
    }

    event.target.parentNode.parentNode.parentNode.replaceChild(formatForm, event.target.parentNode.parentNode)
}

function saveFormat() {

}

function cancelAddingFormat(event) {
    if (event.target.parentNode.querySelector(".save-button").dataset["uuid"] === 'new') {

    } else {

    }
}

/*
<template id="format-form">
        <tr>
            <td class="display-name"><input type="text" /></td>
            <td class="slug"><input type="text" /></td>
            <td class="action">
                <button class="save-button">Save</button>
                <button class="cancel-button">Cancel</button>
                <b
            </td>
        </tr>
    </template>
 */