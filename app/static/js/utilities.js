function getCurrentTimezone(options) {
     for (const option of options) {
         if (option.value === Intl.DateTimeFormat().resolvedOptions().timeZone) {
             option.setAttribute("selected", "true");
         } else {
             option.removeAttribute("selected");
         }
     }
}

let regenerationCheckInterval = {};
function checkRegenerationLock(disabledItems) {
    fetch('/api/post/is-generating', {
        method: 'GET',
        headers: {
            'authorization': document.cookie
                .split(';')
                .find(row => row.trim().startsWith('sloth_session'))
                .split('=')[1]
        }
    }).then(response => {
        if (response.ok) {
            return response.json()
        }
        throw `${response.status}: ${response.statusText}`
    }).then(result => {
        console.log(result);
        if (!result["generating"]) {
            clearInterval(regenerationCheckInterval);
            disabledItems.forEach(button => button.removeAttribute("disabled"));

        }
    }).catch(error => {
        console.error('Error:', error);
    });
}