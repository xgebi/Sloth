document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelector(".dangerzone .delete").addEventListener(
        'click', function (event) {
            event.target.classList.add("hidden");
            document.querySelector(".confirm-deletion").classList.remove("hidden");
        }
    );
    document.querySelector(".dangerzone .confirm-delete").addEventListener(
        'click', function (event) {
            fetch('/api/post-type/delete', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': document.cookie
                        .split(';')
                        .find(row => row.trim().startsWith('sloth_session'))
                        .split('=')[1]
                },
                body: JSON.stringify({
                    current: event.target.dataset['uuid'],
                    action: document.querySelector("#post-type-alt").value
                })
            }).then(response => {
                if (response.ok) {
                    window.location.replace(`${window.location.href.substring(0, window.location.href.lastIndexOf("/"))}s`);
                    return;
                }
                throw `${response.status}: ${response.statusText}`
            }).catch((error) => {
                    console.error('Error:', error);
                });
        }
    );
});