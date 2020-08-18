document.addEventListener('DOMContentLoaded', (event) => {
    // 1. open upload modal
    document.querySelector("#wordpress-import-button").addEventListener('click', uploadFile);
    // 2. upload file

    // 3. delete file query
});

function uploadFile() {
    debugger;
    const formData = new FormData();
    const wpData = document.querySelector('#wordpress-import');
    const wpUploads = document.querySelector('#wordpress-uploads');

    formData.append('data', wpData.files[0]);
    formData.append('uploads', wpUploads.files[0]);

    fetch('/api/content/import/wordpress', {
        method: 'POST',
        headers: {
            'authorization': document.cookie
                .split(';')
                .find(row => row.trim().startsWith('sloth_session'))
                .split('=')[1],
        },
        body: formData
    }).then(response => {
        console.log(response);
        return response.json()
    }).then(data => {
        console.log('Success:', data);
        document.querySelector("#rewrite-rules").innerHTML = data.rules.join("<br />");
    }).catch((error) => {
        console.error('Error:', error);
    })
}

function uploadMedia() {
    const formData = new FormData();
    const fileField = document.querySelector('#file-upload');

    formData.append('image', fileField.files[0]);

    const files = document.querySelector("#wordpress-uploads");
    const reader = new FileReader();
    reader.onload = function (evt) {
        debugger;
        document.querySelector("#wordpress-uploads-button").setAttribute("disabled", "disabled");
        fetch('/api/content/import/wordpress-media', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-zip-compressed',
                'authorization': document.cookie
                    .split(';')
                    .find(row => row.trim().startsWith('sloth_session'))
                    .split('=')[1],
            },
            body: evt.target.result
        }).then(response => {
            console.log(response);
            return response.json()
        }).then(data => {
            console.log('Success:', data);
        }).catch((error) => {
            console.error('Error:', error);
        });
    };
    reader.readAsBinaryString(files.files[0]);
}