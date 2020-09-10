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
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        })
    })
});