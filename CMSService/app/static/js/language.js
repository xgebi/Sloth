let newLangs = 0;

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll(".action-button").forEach(button => {
        button.addEventListener('click', editButtonClick)
    });

    document.querySelectorAll(".delete-button").forEach(button => {
        button.addEventListener('click', deleteLanguage)
    });

    document.querySelector("#create-new-language").addEventListener('click', addNewLanguage)
});

function editButtonClick(event) {
    if (event.target.dataset["action"] === "edit") {
        editAction(event.target)
    } else if (event.target.dataset["action"] === "save") {
        saveAction(event.target)
    }
}

function editAction(button) {
    const longNameText = document.querySelector(`#language-${button.dataset['uuid']} .language-long-name`).textContent;
    const shortNameText = document.querySelector(`#language-${button.dataset['uuid']} .language-short-name`).textContent;

    const longNameInput = document.createElement('input');
    longNameInput.setAttribute("type", "text");
    longNameInput.value = longNameText;

    const shortNameInput = document.createElement('input');
    shortNameInput.setAttribute("type", "text");
    shortNameInput.value = shortNameText;

    const longNameTd = document.querySelector(`#language-${button.dataset['uuid']} .language-long-name`);
    const shortNameTd = document.querySelector(`#language-${button.dataset['uuid']} .language-short-name`);

    while (longNameTd.firstChild) {
        longNameTd.removeChild(longNameTd.lastChild);
    }
    longNameTd.appendChild(longNameInput);
    while (shortNameTd.firstChild) {
        shortNameTd.removeChild(shortNameTd.lastChild);
    }
    shortNameTd.appendChild(shortNameInput);

    button.dataset["action"] = "save";
    button.textContent = "Save"
}

function saveAction(button) {
    const longName = document.querySelector(`#language-${button.dataset['uuid']} .language-long-name input`).value;
    const shortName = document.querySelector(`#language-${button.dataset['uuid']} .language-short-name input`).value;

    fetch(`/api/settings/language/${button.dataset['uuid']}/save`, {
        method: 'POST',
        headers: {
            'authorization': document.cookie
                .split(';')
                .find(row => row.trim().startsWith('sloth_session'))
                .split('=')[1]
        },
        body: JSON.stringify({
            longName,
            shortName
        })
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
        throw `${response.status}: ${response.statusText}`;
    }).then(result => {
        document.querySelector(`#language-${button.dataset['uuid']} .language-long-name`).textContent = result["longName"];
        document.querySelector(`#language-${button.dataset['uuid']} .language-short-name`).textContent = result["shortName"];
        button.dataset["action"] = "edit";
    button.textContent = "Edit"
    }).catch(err => {
        console.log(err)
    })
}

function addNewLanguage(event) {
    newLangs++;
    const tbody = document.querySelector("#language-table tbody");
    const tr = document.createElement('tr');
    tr.setAttribute("id", `language-new-${newLangs}`);
    const longNameTd = document.createElement('td');
    longNameTd.setAttribute("class", "language-long-name");
    const shortNameTd = document.createElement('td');
    shortNameTd.setAttribute("class", "language-short-name");

    const longNameInput = document.createElement('input');
    longNameInput.setAttribute("type", "text");

    const shortNameInput = document.createElement('input');
    shortNameInput.setAttribute("type", "text");

    longNameTd.appendChild(longNameInput);
    shortNameTd.appendChild(shortNameInput);

    tr.appendChild(longNameTd);
    tr.appendChild(shortNameTd);

    tr.appendChild(document.createElement("td"));

    const buttonSave = document.createElement('button');
    buttonSave.dataset["action"] = "save";
    buttonSave.textContent = "Save";
    buttonSave.setAttribute("class", "action-button");
    buttonSave.setAttribute("data-uuid", `new-${newLangs}`);
    buttonSave.addEventListener('click', editButtonClick);

    const buttonSaveTd = document.createElement("td");
    buttonSaveTd.appendChild(buttonSave);

    tr.appendChild(buttonSaveTd);

    const buttonDelete = document.createElement('button');
    buttonDelete.textContent = "Delete";
    buttonDelete.setAttribute("class", "delete-button");
    buttonDelete.setAttribute("data-uuid", "new");
    buttonDelete.addEventListener('click', deleteLanguage);

    const buttonDeleteTd = document.createElement("td");
    buttonDeleteTd.appendChild(buttonDelete);

    tr.appendChild(buttonDeleteTd);

    tbody.appendChild(tr)
}

function deleteLanguage(event) {
    if (event.target.dataset["uuid"] === "new") {
        document.querySelector("#language-table tbody").removeChild(event.target.parentNode.parentNode);
    } else {
        fetch(`/api/settings/language/${event.target.dataset["uuid"]}/delete`, {
            method: 'DELETE',
            headers: {
                'authorization': document.cookie
                    .split(';')
                    .find(row => row.trim().startsWith('sloth_session'))
                    .split('=')[1]
            }
        }).then(response => {
            if (response.ok) {
                document.querySelector("#language-table tbody").removeChild(event.target.parentNode.parentNode);
            }
            throw `${response.status}: ${response.statusText}`;
        }).catch(err => {
            console.log(err)
        })
    }
}
