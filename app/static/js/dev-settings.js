document.addEventListener('DOMContentLoaded', (event) => {
    // 1. open upload modal
    document.querySelector("#delete-button").addEventListener('click', deleteDbContent);
    document.querySelector("#unlock-generation-button").addEventListener('click', deleteGenerationLock);
    // 2. upload file

    // 3. delete file query
});
/*
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

function deleteGenerationLock() {
    fetch('/api/settings/generation-lock', {
        method: 'DELETE',
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
}*/
