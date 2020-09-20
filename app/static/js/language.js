document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll(".action-button").forEach(button => {
        button.addEventListener('click', (event) => {
            if (button.dataset["action"] === "edit") {
                editAction(button)
            } else if (button.dataset["action"] === "save") {
                saveAction(button)
            }
        })
    })
});

function editAction(button) {
    const longNameText = document.querySelector(`#language-${button.dataset['uuid']} .language-long-name`).textContent;
    const shortNameText = document.querySelector(`#language-${button.dataset['uuid']} .language-short-name`).textContent;

    const longNameInput = document.createElement('input');
    longNameInput.setAttribute("type", "text");
    longNameInput.value = longNameText;

    const shortNameInput = document.createElement('input');
    shortNameInput.setAttribute("type", "text");
    shortNameInput.value = shortNameText;

    debugger;
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