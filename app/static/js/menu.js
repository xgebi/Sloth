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
                    if (response.status === 200) {
                        return response.json()
                    } else {
                        throw "Server error" // may be?
                    }
                })
                .then(data => {
                    console.log(data)
                    setupMenuForEdit(data, editButtons.dataset["name"], editButtons.dataset["uuid"]);
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        })
    })
});

function setupMenuForEdit(menuData, name, uuid) {
    debugger;
    if ('content' in document.createElement('template')) {
        const menuWrapper = document.querySelector("#menu-wrapper");
        const formTemplate = document.querySelector('#menu-form');
        const itemTemplate = document.querySelector('#item-row');

        const formClone = formTemplate.content.cloneNode(true);
        const nameInput = formClone.querySelector("#name");
        nameInput.setAttribute("data-uuid", uuid);
        nameInput.setAttribute("data-old-name", name);
        nameInput.value = name;

        const tbody = formTemplate.querySelector("tbody");
        for (const itemData of menuData) {
            const item = itemTemplate.content.cloneNode(true);

        }


        menuWrapper.appendChild(formClone);
    }
}