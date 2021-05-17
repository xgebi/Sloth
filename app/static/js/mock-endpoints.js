document.addEventListener('DOMContentLoaded', function() {
   const deleteButton = document.querySelector("#delete-button"); // .dataset["posttypeUuid"]
    deleteButton.addEventListener('click', () => {
        fetch(`${apiUrl}/api/mock-endpoints/${deleteButton.dataset["uuid"]}/delete`, {
            method: 'DELETE',
            headers: {
                'authorization': document.cookie
                    .split(';')
                    .find(row => row.trim().startsWith('sloth_session'))
                    .split('=')[1]
            }
        }).then(response => {
            if (response.status === 204) {
                window.location.replace(window.location.href.substring(0, window.location.href.lastIndexOf("/")));
            }
            return response.json();
        }).then(result => {
            const error = document.createElement("p")
            error.textContent = "Error deleting endpoint"
            deleteButton.parentNode.appendChild(error)
        }).catch(error => {
            console.error('Error:', error);
        });
    });
});