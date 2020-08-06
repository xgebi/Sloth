document.addEventListener('DOMContentLoaded', (event) => {
    // 1. open upload modal
    document.querySelector("#wordpress-import-button").addEventListener('click', uploadFile);

    // 2. upload file

    // 3. delete file query
});

function uploadFile() {
    const files = document.querySelector("#wordpress-import");
    const reader = new FileReader();
    reader.onload = function (evt) {
        console.log(evt.target.result);
        document.querySelector("#wordpress-import-button").setAttribute("disabled", "disabled");
        fetch('/api/content/import/wordpress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'authorization': document.cookie
                    .split(';')
                    .find(row => row.trim().startsWith('sloth_session'))
                    .split('=')[1],
            },
            body: JSON.stringify({"data": evt.target.result})
        }).then(response => {
            console.log(response);
            return response.json()
        }).then(data => {
            console.log('Success:', data);
            document.querySelector("#rewrite-rules").innerHTML = data.rules.join("<br />");
        }).catch((error) => {
            console.error('Error:', error);
        });
    };
    reader.readAsText(files.files[0]);
}