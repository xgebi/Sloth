document.addEventListener('DOMContentLoaded', (event) => {
    const regenerateAllButton = document.querySelector("#regenerate-all-button");
    regenerateAllButton.addEventListener('click', function () {
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

    const themeUploadButton = document.querySelector("#theme-upload-button");
    themeUploadButton.addEventListener('click', function () {
        const formData = new FormData();
        const fileField = document.querySelector('#file-upload');

        formData.append('image', fileField.files[0]);
        debugger;
        fetch('/api/upload-theme', {
            method: 'POST',
            headers: {
                'authorization': document.cookie
                    .split(';')
                    .find(row => row.trim().startsWith('sloth_session'))
                    .split('=')[1]
            },
            body: formData
        }).then(response => response.json()).then(result => {
            console.log(result);
        }).catch(error => {
            console.error('Error:', error);
        });
    });
});