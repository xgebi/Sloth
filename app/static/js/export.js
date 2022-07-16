document.addEventListener('DOMContentLoaded', (event) => {
    // 1. open upload modal
    document.querySelector("#export-data").addEventListener('click', downloadFile);
});

function downloadFile() {
    fetch('/api/content/export/sloth', { // TODO create the endpoint
        method: 'POST',
        headers: {
            'authorization': document.cookie
                .split(';')
                .find(row => row.trim().startsWith('sloth_session'))
                .split('=')[1],
        }
    }).then(response => {
        if (response.ok) {
            return response.json()
        }
        throw `${response.status}: ${response.statusText}`
    }).then(data => {
        console.log('Success:', data);
    }).catch((error) => {
        console.error('Error:', error);
    })
}