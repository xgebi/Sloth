document.addEventListener('DOMContentLoaded', (event) => {
    // delete-taxonomy
    if (document.querySelector("#delete-taxonomy")) {
        document.querySelector("#delete-taxonomy").addEventListener('click', () => {
            fetch(`/api/post/taxonomy/${document.querySelector("#delete-taxonomy").dataset["uuid"]}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': document.cookie
                        .split(';')
                        .find(row => row.trim().startsWith('sloth_session'))
                        .split('=')[1]
                }
            }).then(response => {
                    if (response.ok) {
                        window.location.replace(window.location.href.substring(0, window.location.href.lastIndexOf("/", window.location.href.lastIndexOf("/") - 1)));
                    }
                    throw `${response.status}: ${response.statusText}`

                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        });
    }

    // display-name
    document.querySelector("#display-name").addEventListener('blur', (event) => {
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
});