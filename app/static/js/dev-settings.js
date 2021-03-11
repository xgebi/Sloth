document.addEventListener('DOMContentLoaded', (event) => {
    // 1. open upload modal
    document.querySelector("#delete-posts")?.addEventListener('click', deletePosts);
    document.querySelector("#delete-taxonomy")?.addEventListener('click', deleteTaxonomy);
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
        method: 'GET',
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
        displayHealthCheckResults(data)
    }).catch((error) => {
        console.error('Error:', error);
    });
}

function displayHealthCheckResults(data) {
    const resultsDiv = document.querySelector("#post-health-check-results");
    while (resultsDiv.lastChild) {
        resultsDiv.removeChild(resultsDiv.lastChild);
    }
    const h2 = document.createElement('h2');
    h2.textContent = "There's issue with following pages";
    resultsDiv.append(h2);
    const ul = document.createElement('ul');
    data["urls"]?.forEach(url => {
        const li = document.createElement('li');
        li.textContent = url;
        ul.append(li)
    });
    resultsDiv.append(ul);
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
