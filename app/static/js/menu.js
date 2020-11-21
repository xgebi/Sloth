document.addEventListener('DOMContentLoaded', () => {
    const editButtons = document.querySelectorAll(".edit-button");
    editButtons.forEach(button => {
        button.addEventListener('click', editMenu)
    });
    document.querySelector("#create-new-menu").addEventListener('click', setupNewMenu);
});

function editMenu(event) {
    const button = event.target;
    fetch(`/settings/themes/menu/${event?.target?.dataset["uuid"]}`, {
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
}

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
        nameInput.value = name;

        formClone.querySelector("#save-menu").addEventListener('click', saveMenu);
        formClone.querySelector("#add-item").addEventListener('click', addNewItem)
        formClone.querySelector("#delete-menu").addEventListener('click', deleteMenu)

        const tbody = formClone.querySelector("tbody");
        menuData.sort((a, b) => {
            return a.position - b.position;
        })
        for (const itemData of menuData) {
            const item = itemTemplate.content.cloneNode(true);
            item.querySelector(".row").setAttribute("data-uuid", itemData.uuid);
            item.querySelector(".item-name input").value = itemData.title;
            item.querySelector(".item-uri input").value = itemData.url;
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

function setupNewMenu(menuData, name, uuid) {
    const menuWrapper = document.querySelector("#menu-wrapper");
    while (menuWrapper.firstChild) {
        menuWrapper.removeChild(menuWrapper.lastChild);
    }

    if ('content' in document.createElement('template')) {
        const formTemplate = document.querySelector('#menu-form');

        const formClone = formTemplate.content.cloneNode(true);
        const nameInput = formClone.querySelector("#name");
        let newMenuIndex = 0;
        for (let i = 0; i < document.querySelector("#menu-table tbody").children.length; i++) {
            if (document.querySelector("#menu-table tbody").children[i].getAttribute("id").startsWith("new-")) {
                newMenuIndex++;
            }
        }
        nameInput.setAttribute("data-uuid", `new-${newMenuIndex + 1}`);

        formClone.querySelector("#save-menu").addEventListener('click', saveMenu);
        formClone.querySelector("#add-item").addEventListener('click', addNewItem)
        formClone.querySelector("#delete-menu").addEventListener('click', deleteMenu)

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
    }

    fetch("/settings/themes/menu/save", {
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
        if (document.querySelector(`#menu-${data["uuid"]}`)) {
            document.querySelector(`#menu-${data["uuid"]} .menu-name`).textContent = data["name"];
        } else {
            const row = document.createElement('tr');
            row.setAttribute("id", `#menu-${data["uuid"]}`);
            const nameColumn = document.createElement('td');
            nameColumn.setAttribute("class", "menu-name");
            nameColumn.textContent = data["name"];
            row.appendChild(nameColumn);
            const actionColumn = document.createElement('td');
            const editButton = document.createElement('button');
            editButton.setAttribute('class', 'edit-button');
            editButton.setAttribute('data-uuid', data["uuid"]);
            editButton.setAttribute('data-name', data["name"]);
            editButton.addEventListener('click', editMenu);
            editButton.textContent = "Edit";
            actionColumn.appendChild(editButton);
            row.appendChild(actionColumn);
            document.querySelector("#menu-table tbody").appendChild(row);
        }
        const menuWrapper = document.querySelector("#menu-wrapper");
        while (menuWrapper.firstChild) {
            menuWrapper.removeChild(menuWrapper.lastChild);
        }
    }).catch(err => {
        console.log(err)
    });
}

function addNewItem() {
    const menuItemsTbody = document.querySelector("#menu-items tbody");
    const itemTemplate = document.querySelector('#item-row');
    const item = itemTemplate.content.cloneNode(true);
    let newItemsCount = 0;
    for (let i = 0; i < menuItemsTbody.children.length; i++) {
        if (menuItemsTbody.children[i].dataset["uuid"].startsWith("new-")) {
            newItemsCount++;
        }
    }
    item.querySelector(".row").setAttribute("data-uuid", `new-${newItemsCount + 1}`);
    menuItemsTbody.appendChild(item);
}

function deleteMenu() {
    const uuid = document.querySelector("#name").dataset["uuid"];
    if (uuid.startsWith("new-")) {
        const menuWrapper = document.querySelector("#menu-wrapper");
        while (menuWrapper.firstChild) {
            menuWrapper.removeChild(menuWrapper.lastChild);
        }
    } else {
        fetch(`/settings/themes/menu/delete`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'authorization': document.cookie
                .split(';')
                .find(row => row.trim().startsWith('sloth_session'))
                .split('=')[1]
        },
        body: JSON.stringify({
            menu: uuid
        })
    })
        .then(response => {
            if (response.ok) {
                const rows = document.querySelector("#menu-table tbody").children;
                for (let i = 0; i < rows.length; i++) {
                    if (rows[i].getAttribute("id") === `menu-${uuid}`) {
                        document.querySelector("#menu-table tbody").removeChild(rows[i]);
                        break;
                    }
                }
                const menuWrapper = document.querySelector("#menu-wrapper");
                while (menuWrapper.firstChild) {
                    menuWrapper.removeChild(menuWrapper.lastChild);
                }
            } else {
                throw "Server error" // may be?
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
}