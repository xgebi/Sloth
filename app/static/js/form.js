document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelector("#add-field").addEventListener('click', addFormItem);
    for (const formField of formFields) {
        addFormItem(formField)
    }
    document.querySelector("#save-form").addEventListener('click', saveForm);
});

function addFormItem(formField) {
    if (typeof(formField.preventDefault) === "function") {
        formField = {
            selectValue: "",
            is_required: false,
            label: "",
            name: "",
            options: []
        };
    }
    const wrapper = document.querySelector("#form-fields");
    const fieldTemplate = document.querySelector("#form-item");

    const fieldClone = fieldTemplate.content.cloneNode(true);
    const select = fieldClone.querySelector("select");
    const selectLabel = fieldClone.querySelector("#item-type-label");
    const fieldId = Math.random().toString(16).slice(2);

    selectLabel.setAttribute('for', `item-type-${fieldId}`);
    selectLabel.setAttribute('id', `item-type-label-${fieldId}`);
    select.setAttribute("id", `item-type-${fieldId}`);
    function processSelectEvent(event) {
        const settingsWrapper = event.target.parentNode.parentNode.querySelector(".form-item-settings");
        if (event.target.value === "") {
            return;
        }
        processSelect(event.target, settingsWrapper)
    }
    function processSelect(select, settingsWrapper) {
        while (settingsWrapper.lastChild) {
            settingsWrapper.removeChild(settingsWrapper.lastChild);
        }

        if (select.value === "") {
            return;
        }

        const settingsTemplate = document.querySelector("#general-setting");
        const settingsClone = settingsTemplate.content.cloneNode(true);

        const labelLabel = settingsClone.querySelector(".label label");
        labelLabel.setAttribute("for", `label-input-${fieldId}`);
        const labelInput = settingsClone.querySelector(".label input");
        labelInput.setAttribute("name", `label-input-${fieldId}`);
        labelInput.setAttribute("id", `label-input-${fieldId}`);
        labelInput.value = formField.label;

        const inputLabel = settingsClone.querySelector(".input label");
        inputLabel.setAttribute("name", `label-input-${fieldId}`);
        const inputInput = settingsClone.querySelector(".input input");
        inputInput.setAttribute("name", `label-input-${fieldId}`);
        inputInput.setAttribute("id", `label-input-${fieldId}`);
        inputInput.value = formField.name;
        if (select.value === "select") {
            settingsClone.querySelector(".add-option").classList.remove("hidden");
            settingsClone.querySelector(".options-wrapper").classList.remove("hidden");
        } else {
            settingsClone.querySelector(".add-option").classList.add("hidden");
            settingsClone.querySelector(".options-wrapper").classList.add("hidden");
        }

        settingsWrapper.appendChild(settingsClone);
    };
    select.addEventListener('change', processSelectEvent);

    for (const child of select.options) {
        if (child.value === formField.type) {
            child.setAttribute("selected","");
        }
    }
    if (formField.selectValue === "select") {
        for (const option in formField?.options) {

        }
    } else {
        processSelect(select, fieldClone.querySelector(".form-item-settings"));
    }
    const isRequired = fieldClone.querySelector("#is-required");
    const isRequiredLabel = fieldClone.querySelector("#is-required-label");
    if (formField.is_required) {
        isRequired.setAttribute("checked","checked");
    }
    isRequiredLabel.setAttribute('for', `is-required-${fieldId}`);
    isRequiredLabel.removeAttribute('id');
    isRequired.setAttribute("id", `is-required-${fieldId}`);
    isRequired.setAttribute("name", `is-required-${fieldId}`);

    const deleteButton = fieldClone.querySelector("button.delete");
    deleteButton.addEventListener('click', (event) => {
        event.target.parentNode.parentNode.removeChild(event.target.parentNode);
    })

    wrapper.appendChild(fieldClone);
}

/*
    <template id="option-item">
        <div>
            <label data-for="option"></label>
            <input type="text" data-id="option" data-name="option">
        </div>
    </template>
* */

function saveForm() {
    if (document.querySelector("#form-name").value.length === 0 || document.querySelector("#form-language").value.length === 0) {
        return;
    }
    const fieldsForm = document.querySelectorAll(".form-field");
    const fields = [];
    let i = 1;
    for (const field of fieldsForm) {
        fields.push({
            type: field.querySelector(".item-type").value,
            isRequired: field.querySelector(".is-required").checked,
            label: field.querySelector(".label-input").value,
            name: field.querySelector(".name-input").value,
            position: i
        })
        i++;
    }

    fetch(`/api/forms/${window.location.pathname.substring(window.location.pathname.lastIndexOf("/") + 1)}/save`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'authorization': document.cookie
                .split(';')
                .find(row => row.trim().startsWith('sloth_session'))
                .split('=')[1],
        },
        body: JSON.stringify({
            formName: document.querySelector("#form-name").value,
            language: document.querySelector("#form-language").value,
            fields
        })
    }).then(response => {
        if (response.ok) {
            return response.json()
        }
        throw `${response.status} ${response.statusText}`;
    }).then(data => {

    }).catch(err => {
        console.log(err)
    });
}