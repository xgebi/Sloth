document.addEventListener('DOMContentLoaded', (event) => {
    // 1. open upload modal
    document.querySelector("#delete-button").addEventListener('click', deleteDbContent);
    // 2. upload file

    // 3. delete file query
});

function deleteDbContent() {
    fetch('/api/content/clear', {
        method: 'DELETE',
        headers: {
            'authorization': document.cookie
                .split(';')
                .find(row => row.trim().startsWith('sloth_session'))
                .split('=')[1],
        }
    }).then(response => {
        console.log(response);
        return response.json()
    }).then(data => {
        console.log('Success:', data);
    }).catch((error) => {
        console.error('Error:', error);
    })
}