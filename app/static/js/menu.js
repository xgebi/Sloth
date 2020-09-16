document.addEventListener('DOMContentLoaded', (event) => {
    const editButtons = document.querySelectorAll(".edit-button");
    editButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            fetch(`/settings/themes/menu/${event.target.dataset["uuid"]}`, {
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
                    } else {
                        throw "Server error" // may be?
                    }
                })
                .then(data => {
                    console.log(data)
                    setupMenuForEdit(data, button.dataset["name"], button.dataset["uuid"]);
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        })
    })
});

function setupMenuForEdit(menuData, name, uuid) {
    const menuWrapper = document.querySelector("#menu-wrapper");
    while (menuWrapper.firstChild) {
        menuWrapper.removeChild(menuWrapper.lastChild);
    }

    if ('content' in document.createElement('template')) {
        const formTemplate = document.querySelector('#menu-form');
        const itemTemplate = document.querySelector('#item-row');

        const formClone = formTemplate.content.cloneNode(true);
        const nameInput = formClone.querySelector("#name");
        nameInput.setAttribute("data-uuid", uuid);
        nameInput.setAttribute("data-old-name", name);
        nameInput.value = name;

        const saveButton = formClone.querySelector("#save-menu");
        saveButton.addEventListener('click', saveMenu);

        const tbody = formClone.querySelector("tbody");
        menuData.sort((a, b) => {
            return a.position - b.position;
        })
        for (const itemData of menuData) {
            const item = itemTemplate.content.cloneNode(true);
            item.querySelector(".row").setAttribute("data-uuid", itemData.uuid);
            item.querySelector(".item-name input").value = itemData.title;
            item.querySelector(".item-uri input").value = itemData.title;
            item.querySelectorAll(".item-type > select option").forEach(option => {
                option.removeAttribute("selected");
                if (option.value === itemData.type) {
                    option.setAttribute("selected", true);
                }
            });

            const upButton = item.querySelector(".item-actions .up");
            upButton.setAttribute("data-uuid", itemData.uuid);
            upButton.addEventListener('click', moveItemUp);
            const downButton = item.querySelector(".item-actions .down")
            downButton.setAttribute("data-uuid", itemData.uuid);
            downButton.addEventListener('click', moveItemDown);
            tbody.appendChild(item);
        }


        menuWrapper.appendChild(formClone);
    }
}

function moveItemUp(event) {
    const index = getRowIndex(event.currentTarget.dataset["uuid"]);
    const rows = document.querySelector("#menu-items tbody").children;
    if (index > 0) {
        rows[index].parentNode.insertBefore(rows[index], rows[index - 1]);
    }
}

function moveItemDown(event) {
    console.log("down");
    const index = getRowIndex(event.currentTarget.dataset["uuid"]);
    const rows = document.querySelector("#menu-items tbody").children;
    if (index < rows.length - 1) {
        rows[index].parentNode.insertBefore(rows[index + 1], rows[index]);
    }
}

function getRowIndex(uuid) {
    let index = -1;
    document.querySelectorAll("#menu-items tbody tr").forEach((row, i) => {
        if (row.dataset["uuid"] === uuid) {
            index = i;
        }
    })
    return index;
}

function saveMenu() {
    const rows = document.querySelector("#menu-items tbody").children;
    const items = {
        uuid: document.querySelector("#name").dataset["uuid"],
        name: document.querySelector("#name").value,
        items: []
    }
    for (let i = 0; i < rows.length; i++) {
        items.items.push({
            uuid: rows[i].dataset["uuid"],
            title: rows[i].querySelector(".item-name input")?.value,
            type: rows[i].querySelector(".item-type select")?.value,
            uri: rows[i].querySelector(".item-uri input")?.value,
            position: i

        });
    };
    fetch("/settings/themes/menu/save",{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'authorization': document.cookie
                .split(';')
                .find(row => row.trim().startsWith('sloth_session'))
                .split('=')[1],
        },
        body: JSON.stringify(items)
    }).then(response => {
        if (response.ok) {
            return response.json()
        }
        throw `${response.status} ${response.statusText}`;
    }).then(data => {

    }).catch(err => {
        console.log(err)
    });
}