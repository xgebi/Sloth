document.addEventListener('DOMContentLoaded', (event) => {
    // 1. open upload modal
    document.querySelector("#delete-posts").addEventListener('click', deletePosts);
    document.querySelector("#delete-taxonomy").addEventListener('click', deleteTaxonomy);
    document.querySelector("#post-health-check").addEventListener('click', postHealthCheck);
    // 2. upload file

    // 3. delete file query
});

function deletePosts() {
    fetch('/api/settings/dev/posts', {
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
    });
}

function deleteTaxonomy() {
    fetch('/api/settings/dev/taxonomy', {
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
    });
}

function postHealthCheck() {
    fetch('/api/settings/dev/health-check', {
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
    });
}

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
