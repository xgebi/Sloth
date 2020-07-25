document.addEventListener('DOMContentLoaded', (event) => {
    const regenerateAllButton = document.querySelector("#regenerate-all-button");
    regenerateAllButton.addEventListener('click', function() {
        fetch('/api/post/regenerate-all', {
        method: 'POST',
        headers: {
            'authorization': document.cookie
                .split(';')
                .find(row => row.trim().startsWith('sloth_session'))
                .split('=')[1]
        },
        body: JSON.stringify({regenerateAll: true})
    }).then(response => response.json()).then(result => {
        regenerateAllButton.setAttribute('disabled', 'disabled');
    }).catch(error => {
        console.error('Error:', error);
    });
    });
});